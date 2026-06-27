import sys
from keeplog.db import init_db, create_session, end_session, save_command, search, list_recent, get_command


def main():
    if len(sys.argv) < 2:
        print("Usage: keeplog <command>")
        print("Commands: init, search <query>, recent, get <id>")
        return

    cmd = sys.argv[1]

    if cmd == "init":
        init_db()
        print("Database initialized at ~/.local/share/keeplog/logs.db")

    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: keeplog search <query>")
            return
        results = search(sys.argv[2])
        for r in results:
            print(f"[{r['timestamp']}] {r['command']}")

    elif cmd == "recent":
        results = list_recent()
        for r in results:
            print(f"[{r['timestamp']}] {r['command']}")

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
            if cmd_data['output']:
                print(f"Output:\n{cmd_data['output']}")
        else:
            print("Not found")
