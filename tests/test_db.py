import os
import sqlite3
import stat
import sys
import tempfile
from pathlib import Path

import pytest

from keeplog import db


@pytest.fixture(autouse=True)
def _temp_db(monkeypatch):
    tmpdir = Path(tempfile.mkdtemp())
    monkeypatch.setattr(db, "_data_dir", lambda: tmpdir)
    monkeypatch.setattr(db, "DB_PATH", tmpdir / "logs.db")
    db.init_db()
    yield
    for f in tmpdir.glob("logs.db*"):
        f.unlink()
    tmpdir.rmdir()


def test_init_db():
    assert db.DB_PATH.exists()


def test_db_has_restrictive_permissions():
    mode = stat.S_IMODE(db.DB_PATH.stat().st_mode)
    assert mode == 0o600


def test_create_session():
    sid = db.create_session("test-host")
    assert sid > 0


def test_save_and_get_command():
    sid = db.create_session()
    cid = db.save_command(sid, 1, "ls -la", "/home", 0, 100, "full", "total 42\nfile.txt")
    assert cid > 0

    cmd = db.get_command(cid)
    assert cmd is not None
    assert cmd["command"] == "ls -la"
    assert cmd["exit_code"] == 0
    assert cmd["output"] == "total 42\nfile.txt"


def test_light_mode_no_output():
    sid = db.create_session()
    cid = db.save_command(sid, 1, "ls", "/home", 0, mode="light", output_content="should not save")
    cmd = db.get_command(cid)
    assert cmd["output"] is None


def test_search():
    sid = db.create_session()
    db.save_command(sid, 1, "docker build .", "/proj", 0, 2000, "full", "Step 1/5")
    db.save_command(sid, 2, "docker ps", "/proj", 0, 50, "full", "CONTAINER ID")
    db.save_command(sid, 3, "ls", "/home", 0, 10, "full", "file.txt")

    results = db.search("docker")
    assert len(results) == 2

    results = db.search("build")
    assert len(results) == 1
    assert results[0]["command"] == "docker build ."


def test_search_matches_output():
    sid = db.create_session()
    db.save_command(sid, 1, "docker ps", "/proj", 0, 50, "full", "b812e0a1f223   postgres:15   Up 2 minutes")
    db.save_command(sid, 2, "ls", "/home", 0, 10, "full", "file.txt")

    results = db.search("postgres")
    assert [r["command"] for r in results] == ["docker ps"]


def test_search_match_in_command_and_output_appears_once():
    sid = db.create_session()
    db.save_command(sid, 1, "docker ps", "/proj", 0, 50, "full", "docker daemon is running")
    assert len(db.search("docker")) == 1


def test_clear_old_removes_output_from_search():
    sid = db.create_session()
    db.save_command(sid, 1, "docker ps", "/proj", 0, 50, "full", "postgres:15")
    conn = db._get_conn()
    conn.execute("UPDATE commands SET timestamp = datetime('now', '-60 days')")
    conn.commit()
    conn.close()

    db.clear_old(30)

    assert db.search("postgres") == []
    conn = db._get_conn()
    conn.execute("INSERT INTO output_fts(output_fts) VALUES('integrity-check')")
    conn.close()


def test_existing_database_gets_output_indexed():
    sid = db.create_session()
    conn = sqlite3.connect(str(db.DB_PATH))
    conn.executescript("""
        DROP TRIGGER output_ai;
        DROP TRIGGER output_ad;
        DROP TRIGGER output_au;
        DROP TABLE output_fts;
    """)
    conn.execute(
        "INSERT INTO commands (session_id, sequence, command, cwd) VALUES (?, 1, 'docker ps', '/proj')",
        (sid,),
    )
    conn.execute("INSERT INTO output (command_id, content) VALUES (last_insert_rowid(), 'postgres:15')")
    conn.commit()
    conn.close()

    results = db.search("postgres")
    assert [r["command"] for r in results] == ["docker ps"]


def test_list_recent():
    sid = db.create_session()
    db.save_command(sid, 1, "first", "/", 0)
    db.save_command(sid, 2, "second", "/", 0)
    db.save_command(sid, 3, "third", "/", 0)

    recent = db.list_recent(5)
    assert len(recent) == 3

    limited = db.list_recent(2)
    assert len(limited) == 2


def test_get_stats():
    sid = db.create_session()
    db.save_command(sid, 1, "echo hi", "/", 0)
    stats = db.get_stats()
    assert stats["commands"] == 1
    assert stats["sessions"] == 1


def test_end_session():
    sid = db.create_session()
    db.end_session(sid)
    conn = db._get_conn()
    row = conn.execute("SELECT ended_at FROM sessions WHERE id = ?", (sid,)).fetchone()
    assert row["ended_at"] is not None
    conn.close()


def test_export_all():
    sid = db.create_session()
    db.save_command(sid, 1, "cmd1", "/", 0)
    db.save_command(sid, 2, "cmd2", "/", 0)
    exported = db.export_all()
    assert len(exported) == 2


def test_clear_old():
    sid = db.create_session()
    db.save_command(sid, 1, "old", "/", 0)
    conn = db._get_conn()
    conn.execute("UPDATE commands SET timestamp = datetime('now', '-60 days') WHERE id = 1")
    conn.commit()
    conn.close()

    db.clear_old(30)

    conn = db._get_conn()
    count = conn.execute("SELECT COUNT(*) FROM commands").fetchone()[0]
    conn.close()
    assert count == 0
