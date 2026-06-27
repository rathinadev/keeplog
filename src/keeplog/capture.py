import os
import pty
import select
import signal
import struct
import fcntl
import sys
import termios
import tty
import time
import tempfile
import shutil

from keeplog.db import create_session, end_session, save_command


def _find_shell() -> str:
    return os.environ.get("SHELL", "/bin/bash")


def _shell_name(path: str) -> str:
    return os.path.basename(path).lower()


def _hooks_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "hooks")


def _build_rc(shell_path: str):
    name = _shell_name(shell_path)
    hook_path = os.path.join(_hooks_dir(), f"{name}.sh")
    user_rc = os.path.expanduser(f"~/.{name}rc")

    lines = ["export __KEEPLOG_READY=0"]
    if os.path.exists(user_rc):
        lines.append(f"source {user_rc}")
    lines.append(f"source {hook_path}")
    lines.append("__KEEPLOG_READY=1")

    fd, path = tempfile.mkstemp(prefix=f"keeplog_{name}_", suffix=".sh", text=True)
    with os.fdopen(fd, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def _build_zsh_zdotdir():
    hook_path = os.path.join(_hooks_dir(), "zsh.sh")
    user_zshrc = os.path.expanduser("~/.zshrc")

    zdotdir = tempfile.mkdtemp(prefix="keeplog_zsh_")
    zshrc_path = os.path.join(zdotdir, ".zshrc")
    with open(zshrc_path, "w") as f:
        f.write("export __KEEPLOG_READY=0\n")
        if os.path.exists(user_zshrc):
            f.write(f"source {user_zshrc}\n")
        f.write(f"source {hook_path}\n")
        f.write("__KEEPLOG_READY=1\n")
    return zdotdir


def _setwinsize(fd, rows, cols):
    s = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, s)


def _get_term_size():
    s = struct.pack("HHHH", 0, 0, 0, 0)
    try:
        result = fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, s)
        rows, cols = struct.unpack("HHHH", result)[:2]
        return rows or 24, cols or 80
    except OSError:
        return 24, 80


def _handle_sigwinch(master_fd):
    rows, cols = _get_term_size()
    _setwinsize(master_fd, rows, cols)


def record_session(mode: str = "full"):
    shell = _find_shell()
    shell_bin = _shell_name(shell)

    ctrl_r, ctrl_w = os.pipe()
    os.set_inheritable(ctrl_w, True)

    session_id = create_session()
    rc_path = None
    zdotdir = None

    if shell_bin == "zsh":
        zdotdir = _build_zsh_zdotdir()
    else:
        rc_path = _build_rc(shell)

    pid, master_fd = pty.fork()

    if pid == 0:
        os.environ["KEEPLOG_CTRL_FD"] = str(ctrl_w)
        os.environ["KEEPLOG_SESSION_ID"] = str(session_id)
        os.environ["KEEPLOG_MODE"] = mode
        os.close(ctrl_r)

        if shell_bin == "zsh":
            os.environ["ZDOTDIR"] = zdotdir
            os.execle(shell, shell, "-i", os.environ)
        else:
            os.execle(shell, shell, "--rcfile", rc_path, os.environ)
        os._exit(1)

    os.close(ctrl_w)

    rows, cols = _get_term_size()
    _setwinsize(master_fd, rows, cols)

    def winch(_sig, _frame):
        _setwinsize(master_fd, *_get_term_size())

    signal.signal(signal.SIGWINCH, winch)

    old_term = termios.tcgetattr(sys.stdin.fileno())
    try:
        tty.setraw(sys.stdin.fileno())

        output_buf = bytearray()
        seq = 0
        current_cmd = None
        current_cwd = ""
        current_start = 0.0
        fds = [master_fd, sys.stdin, ctrl_r]

        while True:
            try:
                r, _w, _e = select.select(fds, [], [])
            except InterruptedError:
                continue

            if master_fd in r:
                try:
                    data = os.read(master_fd, 65536)
                except OSError:
                    break
                if not data:
                    break
                output_buf.extend(data)
                try:
                    sys.stdout.buffer.write(data)
                    sys.stdout.buffer.flush()
                except OSError:
                    pass

            if sys.stdin in r:
                try:
                    data = os.read(sys.stdin.fileno(), 65536)
                except OSError:
                    break
                if not data:
                    break
                try:
                    os.write(master_fd, data)
                except OSError:
                    pass

            if ctrl_r in r:
                try:
                    raw = os.read(ctrl_r, 4096)
                except OSError:
                    break
                if not raw:
                    break
                for line in raw.decode("utf-8", errors="replace").split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("C:"):
                        _flush_cmd(
                            session_id, seq, current_cmd,
                            current_cwd, mode, output_buf,
                            current_start,
                        )
                        seq += 1
                        current_cmd = line[2:]
                        current_cwd = os.getcwd()
                        current_start = time.time()
                        output_buf = bytearray()
                    elif line.startswith("E:") and current_cmd is not None:
                        try:
                            ec = int(line[2:])
                        except ValueError:
                            ec = -1
                        _flush_cmd(
                            session_id, seq, current_cmd,
                            current_cwd, mode, output_buf,
                            current_start, ec,
                        )
                        seq += 1
                        current_cmd = None
                        output_buf = bytearray()

    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_term)
        try:
            if rc_path:
                os.remove(rc_path)
            if zdotdir:
                shutil.rmtree(zdotdir, ignore_errors=True)
        except OSError:
            pass
        end_session(session_id)


def _flush_cmd(session_id, seq, command, cwd, mode, output_buf, start_time, exit_code=None):
    if exit_code is None:
        exit_code = -1
    if seq == 0 and not command:
        return
    duration_ms = int((time.time() - start_time) * 1000)
    output = output_buf.decode("utf-8", errors="replace")
    save_command(
        session_id, seq, command or "", cwd or os.getcwd(),
        exit_code, duration_ms, mode, output if mode == "full" else None,
    )
