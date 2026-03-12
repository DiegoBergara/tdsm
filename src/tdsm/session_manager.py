"""Session manager: create, list, get metadata, rename, kill. Integrates tmux, DB, and session context."""

import sqlite3
from datetime import datetime, timezone
from typing import Optional

from tdsm.providers.base import BaseProvider
from tdsm import tmux_controller
from tdsm.session_context import SessionContextStore


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SessionManager:
    """Creates and manages tmux sessions; persists to managed_sessions; updates session context."""

    def __init__(
        self,
        db_path: str,
        context_store: SessionContextStore,
    ):
        self._db_path = db_path
        self._context = context_store

    def create_session(
        self,
        session_name: str,
        provider: BaseProvider,
        working_directory: Optional[str] = None,
    ) -> None:
        """Create tmux session, run provider bootstrap_commands, persist to DB with default mode."""
        if tmux_controller.session_exists(session_name):
            raise ValueError(f"Session already exists: {session_name}")
        tmux_controller.create_session(session_name, working_directory)
        mode = provider.default_mode()
        for cmd in provider.bootstrap_commands():
            tmux_controller.send_keys(session_name, cmd, enter=True)
        conn = sqlite3.connect(self._db_path)
        try:
            now = _utc_now()
            conn.execute(
                """INSERT INTO managed_sessions
                   (session_name, provider_id, mode, working_directory, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (session_name, provider.id, mode, working_directory or "", now, now),
            )
            conn.commit()
        finally:
            conn.close()

    def list_sessions(self) -> list[dict]:
        """Return list of session metadata dicts (session_name, provider_id, mode, ...)."""
        conn = sqlite3.connect(self._db_path)
        try:
            rows = conn.execute(
                """SELECT session_name, provider_id, mode, working_directory, created_at, updated_at
                   FROM managed_sessions ORDER BY session_name"""
            ).fetchall()
            return [
                {
                    "session_name": r[0],
                    "provider_id": r[1],
                    "mode": r[2],
                    "working_directory": r[3] or "",
                    "created_at": r[4],
                    "updated_at": r[5],
                }
                for r in rows
            ]
        finally:
            conn.close()

    def get_session_metadata(self, session_name: str) -> Optional[dict]:
        """Return metadata for session or None if not found."""
        conn = sqlite3.connect(self._db_path)
        try:
            row = conn.execute(
                """SELECT session_name, provider_id, mode, working_directory, created_at, updated_at
                   FROM managed_sessions WHERE session_name = ?""",
                (session_name,),
            ).fetchone()
            if not row:
                return None
            return {
                "session_name": row[0],
                "provider_id": row[1],
                "mode": row[2],
                "working_directory": row[3] or "",
                "created_at": row[4],
                "updated_at": row[5],
            }
        finally:
            conn.close()

    def set_session_mode(self, session_name: str, mode: str) -> None:
        """Update stored mode for session."""
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute(
                "UPDATE managed_sessions SET mode = ?, updated_at = ? WHERE session_name = ?",
                (mode, _utc_now(), session_name),
            )
            conn.commit()
        finally:
            conn.close()

    def rename_session(self, old_name: str, new_name: str) -> None:
        """Rename tmux session and update DB; update context for chats that had old_name as current."""
        meta = self.get_session_metadata(old_name)
        if not meta:
            raise ValueError(f"Session not found: {old_name}")
        if self.get_session_metadata(new_name):
            raise ValueError(f"Session already exists: {new_name}")
        tmux_controller.rename_session(old_name, new_name)
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute(
                """UPDATE managed_sessions SET session_name = ?, updated_at = ? WHERE session_name = ?""",
                (new_name, _utc_now(), old_name),
            )
            conn.commit()
        finally:
            conn.close()
        self._context.rename_current_session(old_name, new_name)

    def kill_session(self, session_name: str) -> None:
        """Kill tmux session, remove from DB, and clear context for chats that had it as current."""
        if not self.get_session_metadata(session_name):
            raise ValueError(f"Session not found: {session_name}")
        tmux_controller.kill_session(session_name)
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute("DELETE FROM managed_sessions WHERE session_name = ?", (session_name,))
            conn.commit()
        finally:
            conn.close()
        self._context.clear_current_if_session(session_name)
