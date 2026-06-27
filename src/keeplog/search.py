import os
import subprocess
import shutil

from keeplog.db import search as db_search, get_command


def _has_fzf() -> bool:
    return shutil.which("fzf") is not None


def search_interactive(query: str):
    results = db_search(query)
    if not results:
        print("No results found")
        return

    if not _has_fzf():
        _print_results(results)
        return

    _fzf_pick(results)


def _print_results(results: list):
    for r in results:
        preview = (r["output_preview"] or "")[:80].replace("\n", " | ")
        print(f"  [{r['id']}] {r['command']}")
        if preview:
            print(f"       {preview}")


def _fzf_pick(results: list):
    lines = [f"{r['id']}  {r['command']}" for r in results]

    preview_cmd = (
        f"keeplog get {{1}}"
    )

    proc = subprocess.Popen(
        [
            "fzf", "--preview", preview_cmd,
            "--preview-window", "right:60%:wrap",
            "--with-nth", "2..",
            "--reverse",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    out, _err = proc.communicate("\n".join(lines))
    if not out:
        return

    cmd_id = out.strip().split(" ")[0]
    cmd_data = get_command(int(cmd_id))
    if cmd_data:
        print(f"Command: {cmd_data['command']}")
        print(f"CWD: {cmd_data['cwd']}")
        print(f"Exit: {cmd_data['exit_code']}")
        print(f"Time: {cmd_data['timestamp']}")
        if cmd_data.get("output"):
            print(f"Output:\n{cmd_data['output']}")
