class Keeplog < Formula
  include Language::Python::Virtualenv

  desc "Terminal session logger that full-text searches output, not just commands"
  homepage "https://github.com/rathinadev/keeplog"
  url "https://files.pythonhosted.org/packages/07/b4/e8b233eff0e1bf208e2a1439a9dc2075282176dde066662dc19e46098061/keeplog-1.1.2.tar.gz"
  sha256 "de219dffd76ec484135c71d09c3cc56e481611ae4413782855dfeb91c0f88909"
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
