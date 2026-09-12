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

1. Publish a new immutable release in [the application repository](https://github.com/gopalasubramanium/plainmark). Never change an existing release tag or silently replace an installer.
2. Verify both architecture downloads, SHA-256 hashes, Developer ID publisher/team, notarization, stapling and Gatekeeper acceptance.
3. Update the version and both hashes in `Casks/plainmark@preview.rb`.
4. Run Homebrew style, audit, fetch and an installation check; review the diff and push the change. Do not add scripts that bypass macOS security checks.
5. Keep release status explicit. A future stable channel should be added only after platform acceptance tests, not by renaming a preview.

Report app problems at [Plainmark issues](https://github.com/gopalasubramanium/plainmark/issues); report packaging issues in this repository. Source, licensing, privacy policy, research and project notes are in [Plainmark](https://github.com/gopalasubramanium/plainmark). This packaging is GPL-3.0-or-later; the app and bundled dependencies retain their respective notices.
