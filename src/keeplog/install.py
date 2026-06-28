import os
import sys
import sysconfig


def _current_shell() -> str:
    return os.path.basename(os.environ.get("SHELL", "/bin/bash")).lower()


def _shell_rc() -> str:
    shell = _current_shell()
    if shell == "zsh":
        return os.path.expanduser("~/.zshrc")
    if shell == "fish":
        return os.path.expanduser("~/.config/fish/config.fish")
    return os.path.expanduser("~/.bashrc")


def _needs_path_fix() -> tuple:
    bin_dir = sysconfig.get_path("scripts")
    path_dirs = os.environ.get("PATH", "").split(":")
    if bin_dir in path_dirs:
        return False, None
    return True, bin_dir


def _hook_line(shell: str) -> str:
    if shell == "fish":
        return '\nif test -z "$KEEPLOG_ACTIVE"; set -gx KEEPLOG_ACTIVE 1; exec keeplog record; end\n'
    return '\nif [[ -z "$KEEPLOG_ACTIVE" ]]; then export KEEPLOG_ACTIVE=1; exec keeplog record; fi\n'


def _path_line(shell: str, bin_dir: str) -> str:
    if shell == "fish":
        return f'\nset -gx PATH "{bin_dir}" $PATH'
    return f'\nexport PATH="{bin_dir}:$PATH"'


def setup_hook():
    shell = _current_shell()
    rc = _shell_rc()
    lines = []

    needs_fix, bin_dir = _needs_path_fix()
    if needs_fix and bin_dir:
        pl = _path_line(shell, bin_dir)
        if os.path.exists(rc):
            with open(rc) as f:
                content = f.read()
            if bin_dir not in content:
                lines.append(pl)
        else:
            lines.append(pl.strip())

    if os.path.exists(rc):
        with open(rc) as f:
            content = f.read()
        if "KEEPLOG_ACTIVE" in content and not needs_fix:
            print(f"Already set up in {rc}")
            return
        with open(rc, "a") as f:
            for line in lines:
                f.write(line + "\n")
            if "KEEPLOG_ACTIVE" not in content:
                f.write(_hook_line(shell))
    else:
        with open(rc, "w") as f:
            for line in lines:
                f.write(line + "\n")
            f.write(_hook_line(shell).strip() + "\n")

    print(f"Setup complete in {rc}")
    if needs_fix and bin_dir:
        print(f"  Added {bin_dir} to PATH")
    print(f"  Auto-start hook added")
    if shell != "fish":
        print("Restart your terminal or run: source " + rc)


def remove_hook():
    rc = _shell_rc()
    if not os.path.exists(rc):
        return
    with open(rc) as f:
        all_lines = f.readlines()
    new_lines = [l for l in all_lines if "KEEPLOG_ACTIVE" not in l]
    if len(new_lines) == len(all_lines):
        print("Not set up")
        return
    with open(rc, "w") as f:
        f.writelines(new_lines)
    print(f"Removed keeplog hook from {rc}")
