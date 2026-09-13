cask "plainmark@preview" do
  arch arm: "aarch64", intel: "x64"

  version "0.4.0"
  sha256 arm:   "02a9005fa25f57b3e68e8795008a9c247820ab1502f76aeeafdc6bf90fa11448",
         intel: "b5a617295b429e08e403e2fff0fd12b36a9fb8b38f265c58344a3766fe75cbdb"

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
