# Plainmark for Homebrew

The official publisher-maintained Homebrew tap for [Plainmark](https://markdown.eksaar.com), a free, open-source Markdown viewer and visual editor. No ads, accounts, telemetry, subscriptions or paid features.

## Install the Mac preview

```sh
brew install --cask gopalasubramanium/plainmark/plainmark@preview
```

Homebrew selects the Apple Silicon or Intel download and verifies its SHA-256 checksum. Both v0.3.3 Mac apps and disk images are signed by Gopala Subramanium and Apple-notarized. The release remains a **preview**. This is the project's own tap, not a listing in Homebrew's central cask repository or the Mac App Store.

If Plainmark is already installed manually in Applications, keep your documents and use that installation or move just the existing app aside before installing through Homebrew. Do not use `--force` to overwrite an installation unexpectedly.

## Update or remove

```sh
brew update
brew upgrade --cask gopalasubramanium/plainmark/plainmark@preview
brew uninstall --cask gopalasubramanium/plainmark/plainmark@preview
```

Uninstalling this cask does not delete your documents or deliberately clear unsaved recovery data. Use Plainmark's Privacy settings to clear recovery copies before uninstalling if desired.

## Release maintenance

The main application repository is the single source of code and binaries. This tap contains only installation metadata and verification scripts. Its **Sync published Plainmark release** workflow checks upstream every four hours and can also be run manually from Actions immediately after publishing a release. It ignores drafts, never downgrades, and refuses changed checksums for an already-published version.

A new version is promoted only after both Mac downloads pass size/hash, exact-source GitHub provenance, Developer ID publisher, notarization, Gatekeeper, app identity/version and architecture checks. Homebrew then validates and installs the new cask before the workflow commits the metadata update. The workflow uses this repository's short-lived GitHub token; it needs no cross-repository secret or access to signing keys. If a release is incomplete or verification fails, the existing version stays available and the workflow fails visibly.

The `@preview` channel follows the newest public numbered release, including a stable release when one is eventually published. It does not build the app or copy source code. Homebrew users receive the new version when they run `brew update` and `brew upgrade`; it does not silently update a running application. GitHub may delay scheduled workflows or disable inactive schedules; the manual workflow is the immediate fallback.

Future releases must include the separately attested `Plainmark_VERSION_ARCH_provenance.json` files produced by the main signing workflow. They bind each final disk image to the checked-out app source commit; GitHub's standard manually dispatched workflow attestation alone identifies the workflow commit. The initial v0.3.3 hashes were verified and installed before this automation was added and remain unchanged.

For manual maintenance if the workflow is unavailable:

1. Publish a new immutable release in [the application repository](https://github.com/gopalasubramanium/plainmark). Never change an existing release tag or silently replace an installer.
2. Verify both architecture downloads, SHA-256 hashes, Developer ID publisher/team, notarization, stapling and Gatekeeper acceptance.
3. Update the version and both hashes in `Casks/plainmark@preview.rb`.
4. Run Homebrew style, audit, fetch and an installation check; review the diff and push the change. Do not add scripts that bypass macOS security checks.
5. Keep release status explicit. A future stable channel should be added only after platform acceptance tests, not by renaming a preview.

Report app problems at [Plainmark issues](https://github.com/gopalasubramanium/plainmark/issues); report packaging issues in this repository. Source, licensing, privacy policy, research and project notes are in [Plainmark](https://github.com/gopalasubramanium/plainmark). This packaging is GPL-3.0-or-later; the app and bundled dependencies retain their respective notices.
