"""SQLite schema and initialization. Per PRD: managed_sessions, chat_context, command_history."""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS managed_sessions (
    session_name TEXT PRIMARY KEY,
    provider_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    working_directory TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_context (
    chat_id INTEGER PRIMARY KEY,
    current_session TEXT,
    FOREIGN KEY (current_session) REFERENCES managed_sessions(session_name)
);

CREATE TABLE IF NOT EXISTS command_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    session_name TEXT NOT NULL,
    command TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_command_history_session_chat
ON command_history(session_name, chat_id);
CREATE INDEX IF NOT EXISTS ix_command_history_timestamp
ON command_history(timestamp);
"""


def init_db(db_path: str) -> None:
    """Create database file and tables if they do not exist."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def get_connection(db_path: str) -> sqlite3.Connection:
    """Return a connection to the database. Caller must close it."""
    return sqlite3.connect(str(db_path))
