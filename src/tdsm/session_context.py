"""Session context store: get/set current session per chat_id; persist to chat_context; in-memory cache."""

import sqlite3
from typing import Optional


class SessionContextStore:
    """Stores and retrieves the current session per chat. Persists to DB with optional cache."""

    def __init__(self, db_path: str, use_cache: bool = True):
        self._db_path = db_path
        self._use_cache = use_cache
        self._cache: dict[int, Optional[str]] = {}

    def get_current_session(self, chat_id: int) -> Optional[str]:
        """Return the current session name for this chat, or None."""
        if self._use_cache and chat_id in self._cache:
            return self._cache[chat_id]
        conn = sqlite3.connect(self._db_path)
        try:
            row = conn.execute(
                "SELECT current_session FROM chat_context WHERE chat_id = ?",
                (chat_id,),
            ).fetchone()
            current = row[0] if row and row[0] else None
            if self._use_cache:
                self._cache[chat_id] = current
            return current
        finally:
            conn.close()

    def set_current_session(self, chat_id: int, session_name: Optional[str]) -> None:
        """Set the current session for this chat. Pass None to clear."""
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute(
                "INSERT INTO chat_context (chat_id, current_session) VALUES (?, ?)"
                " ON CONFLICT(chat_id) DO UPDATE SET current_session = excluded.current_session",
                (chat_id, session_name),
            )
            conn.commit()
            if self._use_cache:
                self._cache[chat_id] = session_name
        finally:
            conn.close()

    def clear_current_if_session(self, session_name: str) -> None:
        """Clear current_session for any chat that has this session as current (e.g. after kill/rename)."""
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute(
                "UPDATE chat_context SET current_session = NULL WHERE current_session = ?",
                (session_name,),
            )
            conn.commit()
            for cid, name in list(self._cache.items()):
                if name == session_name:
                    self._cache[cid] = None
        finally:
            conn.close()

    def update_current_if_was(self, chat_id: int, old_name: str, new_name: str) -> None:
        """If current session for chat was old_name, set it to new_name (e.g. after rename)."""
        current = self.get_current_session(chat_id)
        if current == old_name:
            self.set_current_session(chat_id, new_name)
