class Keeplog < Formula
  include Language::Python::Virtualenv

  desc "Terminal session logger that full-text searches output, not just commands"
  homepage "https://github.com/rathinadev/keeplog"
  url "https://files.pythonhosted.org/packages/66/e9/428f33ee41e18134ef5eced748b7a065ba69083b8ff73618075e13fa3d88/keeplog-1.1.1.tar.gz"
  sha256 "82916a08c3095bc55e1d601732623eb8b1786e03df8399a1b54ce43e1bbdf8c1"
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
