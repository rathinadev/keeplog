import os
import sqlite3
import sys
from pathlib import Path
from typing import Optional


def _data_dir() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"
    return base / "keeplog"


DB_PATH = _data_dir() / "logs.db"

OUTPUT_FTS_SCHEMA = """
    CREATE VIRTUAL TABLE IF NOT EXISTS output_fts USING fts5(
        content, content='output', content_rowid='command_id'
    );

    CREATE TRIGGER IF NOT EXISTS output_ai AFTER INSERT ON output BEGIN
        INSERT INTO output_fts(rowid, content) VALUES (new.command_id, new.content);
    END;

    CREATE TRIGGER IF NOT EXISTS output_ad AFTER DELETE ON output BEGIN
        INSERT INTO output_fts(output_fts, rowid, content) VALUES('delete', old.command_id, old.content);
    END;

    CREATE TRIGGER IF NOT EXISTS output_au AFTER UPDATE ON output BEGIN
        INSERT INTO output_fts(output_fts, rowid, content) VALUES('delete', old.command_id, old.content);
        INSERT INTO output_fts(rowid, content) VALUES (new.command_id, new.content);
    END;
"""


def _get_conn() -> sqlite3.Connection:
    _data_dir().mkdir(parents=True, exist_ok=True)
    is_new = not DB_PATH.exists()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    if is_new:
        try:
            os.chmod(DB_PATH, 0o600)
        except OSError:
            pass
    _add_output_search(conn)
    return conn


def _add_output_search(conn: sqlite3.Connection):
    # Databases from older versions have saved output but no index over it.
    names = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE name IN ('output', 'output_fts')"
    )}
    if "output" in names and "output_fts" not in names:
        conn.executescript(
            "BEGIN IMMEDIATE;"
            + OUTPUT_FTS_SCHEMA
            + "INSERT INTO output_fts(output_fts) VALUES('rebuild');"
            + "COMMIT;"
        )


def _db_exists() -> bool:
    return DB_PATH.exists()


def ensure_db():
    if not _db_exists():
        init_db()


def init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            started_at TEXT NOT NULL DEFAULT (datetime('now')),
            ended_at TEXT,
            hostname TEXT
        );

        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY,
            session_id INTEGER NOT NULL,
            sequence INTEGER NOT NULL,
            command TEXT NOT NULL,
            cwd TEXT,
            exit_code INTEGER,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            duration_ms INTEGER,
            mode TEXT NOT NULL DEFAULT 'full',
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS commands_fts USING fts5(
            command, cwd, content='commands', content_rowid='id'
        );

        CREATE TRIGGER IF NOT EXISTS commands_ai AFTER INSERT ON commands BEGIN
            INSERT INTO commands_fts(rowid, command, cwd) VALUES (new.id, new.command, new.cwd);
        END;

        CREATE TRIGGER IF NOT EXISTS commands_ad AFTER DELETE ON commands BEGIN
            INSERT INTO commands_fts(commands_fts, rowid, command, cwd) VALUES('delete', old.id, old.command, old.cwd);
        END;

        CREATE TRIGGER IF NOT EXISTS commands_au AFTER UPDATE ON commands BEGIN
            INSERT INTO commands_fts(commands_fts, rowid, command, cwd) VALUES('delete', old.id, old.command, old.cwd);
            INSERT INTO commands_fts(rowid, command, cwd) VALUES (new.id, new.command, new.cwd);
        END;

        CREATE TABLE IF NOT EXISTS output (
            command_id INTEGER PRIMARY KEY,
            content TEXT,
            FOREIGN KEY (command_id) REFERENCES commands(id)
        );
    """ + OUTPUT_FTS_SCHEMA)
    conn.commit()
    conn.close()


def create_session(hostname: str = "") -> int:
    ensure_db()
    conn = _get_conn()
    cur = conn.execute(
        "INSERT INTO sessions (hostname) VALUES (?)", (hostname or "",)
    )
    session_id = cur.lastrowid
    conn.commit()
    conn.close()
    return session_id


def end_session(session_id: int):
    conn = _get_conn()
    conn.execute(
        "UPDATE sessions SET ended_at = datetime('now') WHERE id = ?",
        (session_id,)
    )
    conn.commit()
    conn.close()


def save_command(
    session_id: int,
    sequence: int,
    command: str,
    cwd: str,
    exit_code: int,
    duration_ms: int = 0,
    mode: str = "full",
    output_content: Optional[str] = None,
) -> int:
    conn = _get_conn()
    cur = conn.execute(
        """INSERT INTO commands (session_id, sequence, command, cwd, exit_code, duration_ms, mode)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (session_id, sequence, command, cwd, exit_code, duration_ms, mode),
    )
    cmd_id = cur.lastrowid
    if output_content is not None and mode == "full":
        conn.execute(
            "INSERT INTO output (command_id, content) VALUES (?, ?)",
            (cmd_id, output_content),
        )
    conn.commit()
    conn.close()
    return cmd_id


def search(query: str, limit: int = 50) -> list:
    if not _db_exists():
        return []
    conn = _get_conn()
    rows = conn.execute(
        """SELECT c.id, c.command, c.cwd, c.exit_code, c.timestamp, c.duration_ms, c.mode,
                  substr(o.content, 1, 200) AS output_preview
           FROM commands c
           LEFT JOIN output o ON o.command_id = c.id
           WHERE c.id IN (SELECT rowid FROM commands_fts WHERE commands_fts MATCH ?)
              OR c.id IN (SELECT rowid FROM output_fts WHERE output_fts MATCH ?)
           ORDER BY c.timestamp DESC
           LIMIT ?""",
        (query, query, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_recent(limit: int = 20) -> list:
    if not _db_exists():
        return []
    conn = _get_conn()
    rows = conn.execute(
        """SELECT c.id, c.command, c.cwd, c.exit_code, c.timestamp, c.duration_ms, c.mode,
                  substr(o.content, 1, 200) AS output_preview
           FROM commands c
           LEFT JOIN output o ON o.command_id = c.id
           ORDER BY c.timestamp DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_command(command_id: int) -> Optional[dict]:
    if not _db_exists():
        return None
    conn = _get_conn()
    row = conn.execute(
        """SELECT c.*, o.content AS output
           FROM commands c
           LEFT JOIN output o ON o.command_id = c.id
           WHERE c.id = ?""",
        (command_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_stats() -> dict:
    result = {"commands": 0, "sessions": 0, "storage_bytes": 0, "last_command": None}
    if not _db_exists():
        return result
    conn = _get_conn()
    cur = conn.execute("SELECT COUNT(*) FROM commands")
    result["commands"] = cur.fetchone()[0]
    cur = conn.execute("SELECT COUNT(*) FROM sessions")
    result["sessions"] = cur.fetchone()[0]
    cur = conn.execute("SELECT SUM(LENGTH(content)) FROM output")
    result["storage_bytes"] = cur.fetchone()[0] or 0
    cur = conn.execute(
        "SELECT timestamp FROM commands ORDER BY timestamp DESC LIMIT 1"
    )
    row = cur.fetchone()
    result["last_command"] = row[0] if row else None
    conn.close()
    return result


def get_last_session() -> Optional[list]:
    if not _db_exists():
        return None
    conn = _get_conn()
    row = conn.execute(
        """SELECT c.*, o.content AS output
           FROM commands c
           LEFT JOIN output o ON o.command_id = c.id
           WHERE c.session_id = (SELECT id FROM sessions ORDER BY id DESC LIMIT 1)
           ORDER BY c.sequence ASC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in row] if row else None


def export_all() -> list:
    if not _db_exists():
        return []
    conn = _get_conn()
    rows = conn.execute(
        """SELECT c.*, o.content AS output
           FROM commands c
           LEFT JOIN output o ON o.command_id = c.id
           ORDER BY c.timestamp ASC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_old(before_days: int = 30):
    if not _db_exists():
        return
    conn = _get_conn()
    conn.execute(
        """DELETE FROM output WHERE command_id IN (
            SELECT id FROM commands WHERE timestamp < datetime('now', ?)
        )""",
        (f"-{before_days} days",),
    )
    conn.execute(
        "DELETE FROM commands WHERE timestamp < datetime('now', ?)",
        (f"-{before_days} days",),
    )
    conn.execute(
        "DELETE FROM sessions WHERE id NOT IN (SELECT DISTINCT session_id FROM commands)"
    )
    conn.commit()
    conn.close()
