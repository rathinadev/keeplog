import json
import sys
import signal

from keeplog.db import (
    init_db, search as db_search, list_recent, get_command,
    get_stats, get_last_session, export_all, clear_old,
)
from keeplog.capture import record_session
from keeplog.install import install, uninstall
from keeplog.search import search_interactive
from keeplog.config import load as load_config, save as save_config, get as get_config


def main():
    if len(sys.argv) < 2:
        print("Usage: keeplog <command>")
        print("Commands:")
        print("  record              Start recording session")
        print("  install             Add keeplog to shell rc")
        print("  uninstall           Remove keeplog from shell rc")
        print("  search <query>      Interactive fzf search")
        print("  recent              Show recent commands")
        print("  get <id>            Show full command details")
        print("  status              Show stats")
        print("  last                Show last session")
        print("  export              Export all data as JSON")
        print("  clear <days>        Clear old data (default 30 days)")
        print("  config [key val]    Get/set configuration")
        print("  init                Initialize database")
        return

    cmd = sys.argv[1]

    if cmd == "init":
        init_db()
        print("Database initialized")

    elif cmd == "record":
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        mode = sys.argv[2] if len(sys.argv) > 2 else get_config("mode")
        from keeplog.db import clear_old
        clear_old(get_config("retention_days"))
        record_session(mode)

    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: keeplog search <query>")
            return
        search_interactive(sys.argv[2])

    elif cmd == "recent":
        results = list_recent()
        for r in results:
            print(f"  [{r['id']}] {r['command']}")

    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: keeplog get <id>")
            return
        cmd_data = get_command(int(sys.argv[2]))
        if cmd_data:
            print(f"Command: {cmd_data['command']}")
            print(f"CWD: {cmd_data['cwd']}")
            print(f"Exit: {cmd_data['exit_code']}")
            print(f"Time: {cmd_data['timestamp']}")
            if cmd_data.get("output"):
                print(f"Output:\n{cmd_data['output']}")
        else:
            print("Not found")

    elif cmd == "status":
        s = get_stats()
        print(f"Commands recorded: {s['commands']}")
        print(f"Sessions: {s['sessions']}")
        print(f"Storage: {_fmt_bytes(s['storage_bytes'])}")
        print(f"Last command: {s['last_command'] or 'N/A'}")

    elif cmd == "last":
        cmds = get_last_session()
        if not cmds:
            print("No sessions yet")
            return
        for c in cmds:
            print(f"[{c['sequence']}] {c['command']}  (exit: {c['exit_code']})")

    elif cmd == "export":
        data = export_all()
        json.dump(data, sys.stdout, indent=2, default=str)
        print()

    elif cmd == "clear":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        clear_old(days)
        print(f"Cleared data older than {days} days")

    elif cmd == "install":
        install()

    elif cmd == "uninstall":
        uninstall()

    elif cmd == "config":
        cfg = load_config()
        if len(sys.argv) >= 4:
            save_config({sys.argv[2]: sys.argv[3]})
            print(f"Set {sys.argv[2]} = {sys.argv[3]}")
        else:
            for k, v in cfg.items():
                print(f"  {k} = {v}")

    else:
        print(f"Unknown command: {cmd}")


def _fmt_bytes(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"
