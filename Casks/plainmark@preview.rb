cask "plainmark@preview" do
  arch arm: "aarch64", intel: "x64"

  version "0.3.3"
  sha256 arm:   "b2bb9343e8a3d6c90c50162d9b57ec9a06aecb107cb1026e7ad51e07a27a15e4",
         intel: "eaff19cb169b5699b89f549f6561bd5b5a5fc091e3a5db6c1f593baeae1e3e19"

  url "https://github.com/gopalasubramanium/plainmark/releases/download/v#{version}/Plainmark_#{version}_#{arch}.dmg"
  name "Plainmark Preview"
  desc "Free, local Markdown viewer and visual editor"
  homepage "https://markdown.eksaar.com/"

  livecheck do
    skip "Upstream release sync verifies signatures and checksums before updating this cask"
  end

  depends_on macos: :big_sur

  app "Plainmark.app"

  caveats <<~EOS
    This is Plainmark's preview channel, maintained by its publisher.
    Mac downloads are Developer ID signed and Apple notarized.
    Your Markdown documents stay where you save them.
  EOS
end
