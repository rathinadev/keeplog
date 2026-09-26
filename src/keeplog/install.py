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


# KEEPLOG_ACTIVE holds the terminal keeplog is recording. Comparing it to the
# current terminal (not just checking it is set) lets tmux/screen panes, which
# inherit the variable but get their own terminal, start their own recording.
def _hook_line(shell: str) -> str:
    if shell == "fish":
        return '\nif isatty stdin; and isatty stdout; and test "$KEEPLOG_ACTIVE" != (tty); exec keeplog record; end\n'
    return '\nif [[ -t 0 && -t 1 && "$KEEPLOG_ACTIVE" != "$(tty)" ]]; then exec keeplog record; fi\n'


def _path_line(shell: str, bin_dir: str) -> str:
    if shell == "fish":
        return f'\nset -gx PATH "{bin_dir}" $PATH'
    return f'\nexport PATH="{bin_dir}:$PATH"'


def setup_hook():
    shell = _current_shell()
    rc = _shell_rc()
    hook = _hook_line(shell).strip()

    content = ""
    if os.path.exists(rc):
        with open(rc) as f:
            content = f.read()
    lines = content.splitlines(keepends=True)
    hook_lines = [line for line in lines if "KEEPLOG_ACTIVE" in line]

    needs_fix, bin_dir = _needs_path_fix()
    add_path = bool(needs_fix and bin_dir and bin_dir not in content)
    path_line = _path_line(shell, bin_dir).strip() + "\n" if add_path else ""

    if [line.strip() for line in hook_lines] == [hook] and not add_path:
        print(f"Already set up in {rc}")
        return

    if hook_lines:
        new_lines, replaced = [], False
        for line in lines:
            if "KEEPLOG_ACTIVE" not in line:
                new_lines.append(line)
            elif not replaced:
                new_lines.append(path_line + hook + "\n")
                replaced = True
        new_content = "".join(new_lines)
    else:
        new_content = content
        if new_content and not new_content.endswith("\n"):
            new_content += "\n"
        new_content += ("\n" if new_content else "") + path_line + hook + "\n"

    with open(rc, "w") as f:
        f.write(new_content)

    if hook_lines:
        print(f"Updated the keeplog hook in {rc}")
    else:
        print(f"Setup complete in {rc}")
        print("  Auto-start hook added")
    if add_path:
        print(f"  Added {bin_dir} to PATH")
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
