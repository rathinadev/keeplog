import json

import pytest

from keeplog import cli


def run(monkeypatch, argv):
    monkeypatch.setattr(cli.sys, "argv", ["keeplog"] + argv)
    cli.main()


def test_no_args_prints_usage(monkeypatch, capsys):
    run(monkeypatch, [])
    out = capsys.readouterr().out
    assert "Usage: keeplog" in out


def test_unknown_command(monkeypatch, capsys):
    run(monkeypatch, ["bogus"])
    out = capsys.readouterr().out
    assert "Unknown command: bogus" in out


def test_init(monkeypatch, capsys):
    called = {}
    monkeypatch.setattr(cli, "init_db", lambda: called.setdefault("init", True))
    run(monkeypatch, ["init"])
    out = capsys.readouterr().out
    assert called.get("init") is True
    assert "Database initialized" in out


def test_recent(monkeypatch, capsys):
    monkeypatch.setattr(cli, "list_recent", lambda: [{"id": 1, "command": "ls"}])
    run(monkeypatch, ["recent"])
    out = capsys.readouterr().out
    assert "[1] ls" in out


def test_get_missing_arg(monkeypatch, capsys):
    run(monkeypatch, ["get"])
    out = capsys.readouterr().out
    assert "Usage: keeplog get <id>" in out


def test_get_not_found(monkeypatch, capsys):
    monkeypatch.setattr(cli, "get_command", lambda cid: None)
    run(monkeypatch, ["get", "99"])
    out = capsys.readouterr().out
    assert "Not found" in out


def test_get_found(monkeypatch, capsys):
    monkeypatch.setattr(cli, "get_command", lambda cid: {
        "command": "ls -la", "cwd": "/home", "exit_code": 0,
        "timestamp": "2026-01-01", "output": "file1",
    })
    run(monkeypatch, ["get", "1"])
    out = capsys.readouterr().out
    assert "Command: ls -la" in out
    assert "Output:\nfile1" in out


def test_status(monkeypatch, capsys):
    monkeypatch.setattr(cli, "get_stats", lambda: {
        "commands": 5, "sessions": 2, "storage_bytes": 2048, "last_command": "2026-01-01",
    })
    run(monkeypatch, ["status"])
    out = capsys.readouterr().out
    assert "Commands recorded: 5" in out
    assert "2.0 KB" in out


def test_last_no_sessions(monkeypatch, capsys):
    monkeypatch.setattr(cli, "get_last_session", lambda: None)
    run(monkeypatch, ["last"])
    out = capsys.readouterr().out
    assert "No sessions yet" in out


def test_last_with_commands(monkeypatch, capsys):
    monkeypatch.setattr(cli, "get_last_session", lambda: [
        {"sequence": 0, "command": "ls", "exit_code": 0},
    ])
    run(monkeypatch, ["last"])
    out = capsys.readouterr().out
    assert "[0] ls  (exit: 0)" in out


def test_export(monkeypatch, capsys):
    monkeypatch.setattr(cli, "export_all", lambda: [{"id": 1, "command": "ls"}])
    run(monkeypatch, ["export"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data == [{"id": 1, "command": "ls"}]


def test_clear_default_days(monkeypatch, capsys):
    seen = {}
    monkeypatch.setattr(cli, "clear_old", lambda days: seen.setdefault("days", days))
    run(monkeypatch, ["clear"])
    out = capsys.readouterr().out
    assert seen["days"] == 30
    assert "Cleared data older than 30 days" in out


def test_clear_custom_days(monkeypatch, capsys):
    seen = {}
    monkeypatch.setattr(cli, "clear_old", lambda days: seen.setdefault("days", days))
    run(monkeypatch, ["clear", "7"])
    capsys.readouterr()
    assert seen["days"] == 7


def test_setup_and_remove(monkeypatch):
    called = []
    monkeypatch.setattr(cli, "setup_hook", lambda: called.append("setup"))
    monkeypatch.setattr(cli, "remove_hook", lambda: called.append("remove"))
    run(monkeypatch, ["setup"])
    run(monkeypatch, ["remove"])
    assert called == ["setup", "remove"]


def test_config_get(monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_config", lambda: {"mode": "full", "retention_days": 30})
    run(monkeypatch, ["config"])
    out = capsys.readouterr().out
    assert "mode = full" in out
    assert "retention_days = 30" in out


def test_config_set(monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_config", lambda: {"mode": "full"})
    seen = {}
    monkeypatch.setattr(cli, "save_config", lambda d: seen.update(d))
    run(monkeypatch, ["config", "mode", "light"])
    out = capsys.readouterr().out
    assert seen == {"mode": "light"}
    assert "Set mode = light" in out
