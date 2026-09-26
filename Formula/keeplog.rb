class Keeplog < Formula
  include Language::Python::Virtualenv

  desc "Terminal session logger that full-text searches output, not just commands"
  homepage "https://github.com/rathinadev/keeplog"
  url "https://files.pythonhosted.org/packages/51/8e/96cdac97bf15891c3ac35969962bfb3e9e53f7557efc248953eb94bc6b94/keeplog-1.1.0.tar.gz"
  sha256 "28b62dd046e38badf8507e30988edba23c5926210c17be22639eadd55f8ce2db"
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
