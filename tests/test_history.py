"""Tests for history_store append and query."""

import pytest

from tdsm.history_store import HistoryStore


def test_append_and_get_last(db_path):
    store = HistoryStore(db_path)
    store.append(chat_id=1, session_name="api", command="npm run dev")
    store.append(chat_id=1, session_name="api", command="ls")
    entries = store.get_last_for_session("api", limit=10, chat_id=1)
    assert len(entries) == 2
    cmds = [e[0] for e in entries]
    assert "npm run dev" in cmds
    assert "ls" in cmds


def test_get_last_for_session_no_chat_filter(db_path):
    store = HistoryStore(db_path)
    store.append(chat_id=1, session_name="s1", command="a")
    store.append(chat_id=2, session_name="s1", command="b")
    entries = store.get_last_for_session("s1", limit=10, chat_id=None)
    assert len(entries) == 2
