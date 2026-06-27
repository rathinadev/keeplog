import sys
import signal

from keeplog.db import init_db, search, list_recent, get_command
from keeplog.capture import record_session


def main():
    if len(sys.argv) < 2:
        print("Usage: keeplog <command>")
        print("Commands: record, search <query>, recent, get <id>, init")
        return

    cmd = sys.argv[1]

    if cmd == "init":
        init_db()
        print("Database initialized")

    elif cmd == "record":
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        mode = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] == "light" else "full"
        record_session(mode)

    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: keeplog search <query>")
            return
        results = search(sys.argv[2])
        for r in results:
            preview = r["output_preview"] or ""
            nl = preview.find("\n")
            if nl != -1:
                preview = preview[:nl] + "..."
            print(f"  [{r['id']}] {r['command']}  ({preview})")

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
