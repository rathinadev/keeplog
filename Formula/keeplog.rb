class Keeplog < Formula
  include Language::Python::Virtualenv

  desc "Terminal session logger that full-text searches output, not just commands"
  homepage "https://github.com/rathinadev/keeplog"
  url "https://files.pythonhosted.org/packages/40/8e/9f940311e8bdb6ee7723a70c4f63ff280a369b4673b87e7e3b7e96a3ebed/keeplog-1.0.0.tar.gz"
  sha256 "cf633941f443a4dbfc7ce675d8172b43ae138ef963204e6634f1efc78fc604cd"
  license "MIT"

  depends_on "python@3.14"
  depends_on "fzf" => :recommended

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"keeplog", "init"
    assert_match "Commands recorded", shell_output("#{bin}/keeplog status")
  end
end
