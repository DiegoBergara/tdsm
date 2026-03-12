"""Tests for session context get/set and persistence."""

import pytest

from tdsm.session_context import SessionContextStore


def test_get_set_current_session(db_path):
    store = SessionContextStore(db_path, use_cache=True)
    assert store.get_current_session(100) is None
    store.set_current_session(100, "api")
    assert store.get_current_session(100) == "api"
    store.set_current_session(100, None)
    assert store.get_current_session(100) is None


def test_persistence_across_store_instances(db_path):
    store1 = SessionContextStore(db_path, use_cache=True)
    store1.set_current_session(200, "mysession")
    store2 = SessionContextStore(db_path, use_cache=False)
    assert store2.get_current_session(200) == "mysession"


def test_clear_current_if_session(db_path):
    store = SessionContextStore(db_path, use_cache=True)
    store.set_current_session(300, "old")
    store.clear_current_if_session("old")
    assert store.get_current_session(300) is None


def test_rename_current_session(db_path):
    store = SessionContextStore(db_path, use_cache=True)
    store.set_current_session(400, "before")
    store.rename_current_session("before", "after")
    assert store.get_current_session(400) == "after"
