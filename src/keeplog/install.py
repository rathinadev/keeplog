import os
import sys
import sysconfig


def _shell_rc() -> str:
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return os.path.expanduser("~/.zshrc")
    return os.path.expanduser("~/.bashrc")


def _needs_path_fix() -> tuple:
    bin_dir = sysconfig.get_path("scripts")
    path_dirs = os.environ.get("PATH", "").split(":")
    if bin_dir in path_dirs:
        return False, None
    return True, bin_dir


_HOOK_LINE = '\nif [[ -z "$KEEPLOG_ACTIVE" ]]; then export KEEPLOG_ACTIVE=1; exec keeplog record; fi\n'


def setup_hook():
    rc = _shell_rc()
    lines = []

    needs_fix, bin_dir = _needs_path_fix()
    if needs_fix and bin_dir:
        path_line = f'\nexport PATH="{bin_dir}:$PATH"'
        if os.path.exists(rc):
            with open(rc) as f:
                content = f.read()
            if bin_dir not in content:
                lines.append(path_line)
        else:
            lines.append(path_line.strip())

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
                f.write(_HOOK_LINE)
    else:
        with open(rc, "w") as f:
            for line in lines:
                f.write(line + "\n")
            f.write(_HOOK_LINE.strip() + "\n")

    print(f"Setup complete in {rc}")
    if needs_fix and bin_dir:
        print(f"  Added {bin_dir} to PATH")
    print(f"  Auto-start hook added")
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
