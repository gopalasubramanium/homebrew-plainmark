#!/usr/bin/env python3
"""Update installation metadata only after verifying upstream release artifacts."""
import hashlib
import json
from pathlib import Path
import plistlib
import re
import subprocess
import tempfile

UPSTREAM = 'gopalasubramanium/plainmark'
TEAM = 'TF2VBZ3XH7'
ROOT = Path(__file__).resolve().parent.parent

def run(args, **kwargs):
    return subprocess.check_output(args, stderr=subprocess.STDOUT, **kwargs).decode()

def api(path):
    return json.loads(run(['gh', 'api', 'repos/' + UPSTREAM + path]))

def version(tag):
    match = re.fullmatch(r'v(\d+)\.(\d+)\.(\d+)', tag)
    if not match:
        raise ValueError('Only explicit vMAJOR.MINOR.PATCH release tags are supported')
    return tuple(map(int, match.groups()))

def select_release(releases):
    eligible = [r for r in releases if not r['draft'] and r.get('published_at')
                and re.fullmatch(r'v\d+\.\d+\.\d+', r['tag_name'])]
    if not eligible:
        raise RuntimeError('No public versioned release is available')
    return max(eligible, key=lambda r: version(r['tag_name']))

def expected_assets(release):
    number = release['tag_name'][1:]
    selected = {}
    for arch in ['aarch64', 'x64']:
        name = f'Plainmark_{number}_{arch}.dmg'
        matches = [a for a in release['assets'] if a['name'] == name]
        if len(matches) != 1:
            raise RuntimeError('Missing or ambiguous Mac installer: ' + name)
        asset = matches[0]
        if (asset['state'] != 'uploaded' or not 0 < asset['size'] <= 200_000_000
                or not re.fullmatch(r'sha256:[0-9a-f]{64}', asset.get('digest') or '')
                or asset['browser_download_url'] != f'https://github.com/{UPSTREAM}/releases/download/{release["tag_name"]}/{name}'):
            raise RuntimeError('Invalid release asset metadata: ' + name)
        selected[arch] = asset
    return selected

def immutable_asset(asset):
    # download_count and timestamps may change while we download and verify.
    return {key: asset[key] for key in ['id', 'name', 'size', 'digest', 'state', 'browser_download_url']}

def check_source_manifest(record, asset, tag, commit):
    if (record.get('schema') != 1 or record.get('repository') != UPSTREAM
            or record.get('tag') != tag or record.get('source_commit') != commit
            or not re.fullmatch(r'[0-9a-f]{40}', record.get('workflow_commit', ''))
            or record.get('artifact') != {'name': asset['name'], 'size': asset['size'], 'sha256': asset['digest'][7:]}):
        raise RuntimeError('Attested source manifest does not match the release and disk image')

def verify_attestation(path):
    run(['gh', 'attestation', 'verify', str(path), '--repo', UPSTREAM,
         '--signer-workflow', UPSTREAM + '/.github/workflows/signed-macos.yml'])

def sha256(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()

def verify_mac(path, asset, expected_version, arch, tag_commit, scratch):
    if path.stat().st_size != asset['size'] or 'sha256:' + sha256(path) != asset['digest']:
        raise RuntimeError('Installer does not match the published size and digest')
    verify_attestation(path)
    # workflow_dispatch provenance identifies the signing workflow commit, which
    # can differ from the checked-out tag. Require a separately attested binding.
    source = scratch / (path.stem + '_provenance.json')
    run(['gh', 'release', 'download', 'v' + expected_version, '--repo', UPSTREAM,
         '--pattern', source.name, '--dir', str(scratch)])
    if not source.is_file() or source.stat().st_size > 16_384:
        raise RuntimeError('Missing or oversized app-source provenance')
    verify_attestation(source)
    check_source_manifest(json.loads(source.read_text()), asset, 'v' + expected_version, tag_commit)
    for target in [path]:
        run(['codesign', '--verify', '--strict', str(target)])
        details = run(['codesign', '--display', '--verbose=4', str(target)])
        if f'TeamIdentifier={TEAM}\n' not in details or 'Authority=Developer ID Application: Gopala Subramanium (' + TEAM + ')' not in details:
            raise RuntimeError('Unexpected installer publisher')
        run(['xcrun', 'stapler', 'validate', str(target)])
        run(['spctl', '--assess', '--type', 'open', '--context', 'context:primary-signature', str(target)])
    mount = scratch / ('mount-' + arch)
    mount.mkdir()
    run(['hdiutil', 'attach', '-readonly', '-nobrowse', '-mountpoint', str(mount), str(path)])
    try:
        app = mount / 'Plainmark.app'
        run(['codesign', '--verify', '--deep', '--strict', str(app)])
        details = run(['codesign', '--display', '--verbose=4', str(app)])
        flags = re.search(r'flags=0x([0-9a-f]+)\(', details)
        if f'TeamIdentifier={TEAM}\n' not in details or not flags or not int(flags[1], 16) & 0x10000:
            raise RuntimeError('Unexpected app publisher or missing hardened runtime')
        run(['xcrun', 'stapler', 'validate', str(app)])
        run(['spctl', '--assess', '--type', 'execute', str(app)])
        with (app / 'Contents/Info.plist').open('rb') as stream:
            info = plistlib.load(stream)
        if (info.get('CFBundleIdentifier') != 'io.github.gopalasubramanium.plainmark'
                or info.get('CFBundleShortVersionString') != expected_version):
            raise RuntimeError('Downloaded app identity/version differs from release metadata')
        expected_arch = {'aarch64':'arm64','x64':'x86_64'}[arch]
        actual_arch = run(['lipo', '-archs', str(app/'Contents/MacOS/plainmark')]).split()
        if expected_arch not in actual_arch:
            raise RuntimeError('Installer architecture mismatch')
    finally:
        run(['hdiutil', 'detach', str(mount)])

def main():
    releases = json.loads(run(['gh', 'api', '--paginate', '--slurp', 'repos/' + UPSTREAM + '/releases?per_page=100']))
    release = select_release([r for page in releases for r in page])
    assets = expected_assets(release)
    number = release['tag_name'][1:]
    cask = ROOT / 'Casks/plainmark@preview.rb'
    original = cask.read_text()
    current = re.search(r'^  version "(\d+\.\d+\.\d+)"$', original, re.M).group(1)
    current_hashes = re.findall(r'"([0-9a-f]{64})"', original)
    hashes = [assets[a]['digest'][7:] for a in ['aarch64','x64']]
    if version('v' + current) > version(release['tag_name']):
        raise RuntimeError('Refusing to downgrade the cask')
    if current == number:
        if hashes != current_hashes:
            raise RuntimeError('Published files changed for an existing version; refusing to overwrite trusted hashes')
        print('Already synchronized with ' + release['tag_name'])
        return
    tag_commit = api('/commits/' + release['tag_name'])['sha']
    with tempfile.TemporaryDirectory(prefix='plainmark-release-') as temporary:
        scratch = Path(temporary)
        for arch, asset in assets.items():
            run(['gh','release','download',release['tag_name'],'--repo',UPSTREAM,'--pattern',asset['name'],'--dir',str(scratch)])
            verify_mac(scratch/asset['name'], asset, number, arch, tag_commit, scratch)
    # Re-read before changing the cask, so a concurrent edit cannot silently alter the selected release.
    fresh = api('/releases/' + str(release['id']))
    if (fresh['draft'] or not fresh.get('published_at') or fresh['tag_name'] != release['tag_name']
            or {a:immutable_asset(v) for a,v in expected_assets(fresh).items()} != {a:immutable_asset(v) for a,v in assets.items()}
            or api('/commits/' + release['tag_name'])['sha'] != tag_commit):
        raise RuntimeError('The upstream release changed during verification')
    updated = original.replace(f'  version "{current}"', f'  version "{number}"', 1)
    for old, new in zip(current_hashes, hashes):
        updated = updated.replace(old, new, 1)
    cask.write_text(updated)
    (ROOT / 'release-sync.json').write_text(json.dumps({
        'repository':UPSTREAM, 'release_id':release['id'], 'tag':release['tag_name'],
        'source_commit':tag_commit, 'prerelease':release['prerelease'],
        'assets':{a:{'id':v['id'],'sha256':v['digest'][7:]} for a,v in assets.items()},
        'verified':['size','SHA-256','GitHub provenance/source commit','Developer ID/team','notarization/stapling','Gatekeeper','app identity/version/architecture']
    },indent=2)+'\n')
    print('Verified and prepared ' + release['tag_name'])

if __name__ == '__main__':
    main()
