import os
import sys


def _shell_rc() -> str:
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return os.path.expanduser("~/.zshrc")
    return os.path.expanduser("~/.bashrc")


_INSTALL_LINE = '\nif [[ -z "$KEEPLOG_ACTIVE" ]]; then export KEEPLOG_ACTIVE=1; exec keeplog record; fi\n'


def install():
    rc = _shell_rc()
    line = _INSTALL_LINE

    if os.path.exists(rc):
        with open(rc) as f:
            content = f.read()
        if "KEEPLOG_ACTIVE" in content:
            print(f"Already installed in {rc}")
            return
        with open(rc, "a") as f:
            f.write(line)
    else:
        with open(rc, "w") as f:
            f.write(line)

    print(f"Installed keeplog hook in {rc}")
    print("Restart your terminal or run: source " + rc)


def uninstall():
    rc = _shell_rc()
    if not os.path.exists(rc):
        return
    with open(rc) as f:
        lines = f.readlines()
    new_lines = [l for l in lines if "KEEPLOG_ACTIVE" not in l]
    if len(new_lines) == len(lines):
        print("Not installed")
        return
    with open(rc, "w") as f:
        f.writelines(new_lines)
    print(f"Removed keeplog hook from {rc}")
