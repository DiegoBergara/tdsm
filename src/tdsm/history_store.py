"""History store: append command (chat_id, session_name, command, timestamp) and query last N per session."""

import sqlite3
from datetime import datetime, timezone
from typing import List, Optional, Tuple


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class HistoryStore:
    """Appends commands to command_history and queries by session."""

    def __init__(self, db_path: str):
        self._db_path = db_path

    def append(self, chat_id: int, session_name: str, command: str) -> None:
        """Record a command execution."""
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute(
                "INSERT INTO command_history (chat_id, session_name, command, timestamp) VALUES (?, ?, ?, ?)",
                (chat_id, session_name, command, _utc_now()),
            )
            conn.commit()
        finally:
            conn.close()

    def get_last_for_session(
        self, session_name: str, limit: int = 50, chat_id: Optional[int] = None
    ) -> List[Tuple[str, str]]:
        """
        Return last `limit` entries for session as list of (command, timestamp).
        If chat_id is given, filter by chat_id; otherwise return for any chat.
        """
        conn = sqlite3.connect(self._db_path)
        try:
            if chat_id is not None:
                rows = conn.execute(
                    """SELECT command, timestamp FROM command_history
                       WHERE session_name = ? AND chat_id = ?
                       ORDER BY id DESC LIMIT ?""",
                    (session_name, chat_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT command, timestamp FROM command_history
                       WHERE session_name = ?
                       ORDER BY id DESC LIMIT ?""",
                    (session_name, limit),
                ).fetchall()
            return [(r[0], r[1]) for r in rows]
        finally:
            conn.close()
