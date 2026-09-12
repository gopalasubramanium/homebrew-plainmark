import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('sync', Path(__file__).with_name('sync-release.py'))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


def release(tag='v0.3.3', draft=False):
    return {'id': 1, 'tag_name': tag, 'draft': draft, 'published_at': '2026-09-12', 'assets': [
        {'id': i, 'name': f'Plainmark_{tag[1:]}_{arch}.dmg', 'state': 'uploaded', 'size': 123,
         'digest': 'sha256:' + str(i) * 64, 'download_count': 0,
         'browser_download_url': f'https://github.com/{sync.UPSTREAM}/releases/download/{tag}/Plainmark_{tag[1:]}_{arch}.dmg'}
        for i, arch in enumerate(['aarch64', 'x64'], 1)]}


class ReleaseTrust(unittest.TestCase):
    def test_newest_numbered_release_excludes_drafts(self):
        self.assertEqual(sync.select_release([release(), release('v0.4.0'), release('v0.5.0', True)])['tag_name'], 'v0.4.0')

    def test_missing_duplicate_malformed_or_redirected_artifacts_are_rejected(self):
        candidates = [release() for _ in range(4)]
        candidates[0]['assets'].pop()
        candidates[1]['assets'].append(candidates[1]['assets'][0])
        candidates[2]['assets'][0]['digest'] = None
        candidates[3]['assets'][0]['browser_download_url'] = 'https://example.invalid/app.dmg'
        for item in candidates:
            with self.subTest(item=item), self.assertRaises(RuntimeError):
                sync.expected_assets(item)

    def test_download_counts_can_change_but_hashes_cannot(self):
        first = release()['assets'][0]
        second = dict(first, download_count=1)
        self.assertEqual(sync.immutable_asset(first), sync.immutable_asset(second))
        second['digest'] = 'sha256:' + 'f' * 64
        self.assertNotEqual(sync.immutable_asset(first), sync.immutable_asset(second))

    def test_provenance_must_bind_exact_app_source_tag_and_file(self):
        asset = release()['assets'][0]
        record = {'schema': 1, 'repository': sync.UPSTREAM, 'tag': 'v0.3.3',
                  'source_commit': 'a' * 40, 'workflow_commit': 'b' * 40,
                  'artifact': {'name': asset['name'], 'size': 123, 'sha256': '1' * 64}}
        sync.check_source_manifest(record, asset, 'v0.3.3', 'a' * 40)
        for field, value in [('source_commit', 'b' * 40), ('tag', 'v0.4.0'),
                             ('repository', 'other/project'), ('artifact', {}), ('schema', 2)]:
            wrong = copy.deepcopy(record)
            wrong[field] = value
            with self.subTest(field=field), self.assertRaises(RuntimeError):
                sync.check_source_manifest(wrong, asset, 'v0.3.3', 'a' * 40)

    def test_current_release_noop_and_tamper_or_downgrade_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'Casks').mkdir()
            cask = root/'Casks/plainmark@preview.rb'
            original = '  version "0.3.3"\n  sha256 arm: "' + '1'*64 + '", intel: "' + '2'*64 + '"\n'
            cask.write_text(original)
            with patch.object(sync, 'ROOT', root), patch.object(sync, 'run', return_value=json.dumps([[release()]])) as run:
                sync.main()
                self.assertEqual(run.call_count, 1)
                self.assertEqual(cask.read_text(), original)
            for candidate in [release('v0.3.2'), release()]:
                candidate['assets'][0]['digest'] = 'sha256:' + 'f'*64
                with patch.object(sync, 'ROOT', root), patch.object(sync, 'run', return_value=json.dumps([[candidate]])), self.assertRaises(RuntimeError):
                    sync.main()
                self.assertEqual(cask.read_text(), original)

    def test_failed_attestation_stops_verification(self):
        with patch.object(sync, 'run', side_effect=RuntimeError('bad attestation')), self.assertRaises(RuntimeError):
            sync.verify_attestation(Path('app.dmg'))


if __name__ == '__main__':
    unittest.main()
