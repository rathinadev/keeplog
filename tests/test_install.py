import tempfile
from pathlib import Path

import pytest

from keeplog import install


@pytest.fixture
def tmp_rc(monkeypatch):
    tmpdir = Path(tempfile.mkdtemp())
    rc = tmpdir / ".bashrc"
    monkeypatch.setattr(install, "_shell_rc", lambda: str(rc))
    monkeypatch.setattr(install, "_current_shell", lambda: "bash")
    monkeypatch.setattr(install, "_needs_path_fix", lambda: (False, None))
    yield rc
    if rc.exists():
        rc.unlink()
    tmpdir.rmdir()


def test_setup_hook_creates_rc_file(tmp_rc):
    install.setup_hook()
    content = tmp_rc.read_text()
    assert "KEEPLOG_ACTIVE" in content
    assert "exec keeplog record" in content


def test_setup_hook_appends_to_existing_rc(tmp_rc):
    tmp_rc.write_text("# existing config\n")
    install.setup_hook()
    content = tmp_rc.read_text()
    assert content.startswith("# existing config\n")
    assert "KEEPLOG_ACTIVE" in content


def test_setup_hook_is_idempotent(tmp_rc, capsys):
    install.setup_hook()
    capsys.readouterr()
    content_after_first = tmp_rc.read_text()

    install.setup_hook()
    out = capsys.readouterr().out

    assert "Already set up" in out
    assert tmp_rc.read_text() == content_after_first


def test_setup_hook_adds_path_fix_when_needed(tmp_rc, monkeypatch):
    monkeypatch.setattr(install, "_needs_path_fix", lambda: (True, "/fake/bin"))
    install.setup_hook()
    content = tmp_rc.read_text()
    assert "/fake/bin" in content
    assert "PATH" in content


def test_remove_hook_removes_lines(tmp_rc):
    install.setup_hook()
    install.remove_hook()
    content = tmp_rc.read_text()
    assert "KEEPLOG_ACTIVE" not in content


def test_remove_hook_when_not_setup(tmp_rc, capsys):
    tmp_rc.write_text("# just a comment\n")
    install.remove_hook()
    out = capsys.readouterr().out
    assert "Not set up" in out


def test_remove_hook_missing_rc_file(monkeypatch, tmp_path):
    rc = tmp_path / "doesnotexist.rc"
    monkeypatch.setattr(install, "_shell_rc", lambda: str(rc))
    install.remove_hook()  # should not raise


def test_shell_rc_paths(monkeypatch):
    monkeypatch.setattr(install, "_current_shell", lambda: "zsh")
    assert install._shell_rc().endswith(".zshrc")

    monkeypatch.setattr(install, "_current_shell", lambda: "fish")
    assert install._shell_rc().endswith("config.fish")

    monkeypatch.setattr(install, "_current_shell", lambda: "bash")
    assert install._shell_rc().endswith(".bashrc")


def test_hook_line_contains_keeplog_active():
    assert "KEEPLOG_ACTIVE" in install._hook_line("bash")
    assert "KEEPLOG_ACTIVE" in install._hook_line("fish")


def test_hook_line_compares_against_current_terminal():
    assert '"$KEEPLOG_ACTIVE" != "$(tty)"' in install._hook_line("bash")
    assert '"$KEEPLOG_ACTIVE" != (tty)' in install._hook_line("fish")


OLD_HOOK = 'if [[ -z "$KEEPLOG_ACTIVE" ]]; then export KEEPLOG_ACTIVE=1; exec keeplog record; fi\n'


def test_setup_hook_upgrades_old_hook_in_place(tmp_rc, capsys):
    tmp_rc.write_text("# before\n" + OLD_HOOK + "# after\n")
    install.setup_hook()
    out = capsys.readouterr().out

    assert "Updated" in out
    assert tmp_rc.read_text() == "# before\n" + install._hook_line("bash").strip() + "\n# after\n"


def test_setup_hook_after_upgrade_is_idempotent(tmp_rc, capsys):
    tmp_rc.write_text(OLD_HOOK)
    install.setup_hook()
    upgraded = tmp_rc.read_text()
    capsys.readouterr()

    install.setup_hook()

    assert "Already set up" in capsys.readouterr().out
    assert tmp_rc.read_text() == upgraded
