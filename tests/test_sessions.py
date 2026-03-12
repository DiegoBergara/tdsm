"""Tests for session creation, list, use, current, rename, kill. Mock tmux and DB."""

import pytest

from tdsm.session_context import SessionContextStore
from tdsm.session_manager import SessionManager
from tdsm.providers import ProviderRegistry, register_builtin_providers


@pytest.fixture(autouse=True)
def mock_tmux(monkeypatch):
    """Mock tmux so tests don't require real tmux."""
    from tdsm import tmux_controller
    created = set()
    monkeypatch.setattr(tmux_controller, "session_exists", lambda s: s in created)
    def create(name, w=None):
        created.add(name)
    monkeypatch.setattr(tmux_controller, "create_session", create)
    monkeypatch.setattr(tmux_controller, "kill_session", lambda s: created.discard(s))
    monkeypatch.setattr(tmux_controller, "rename_session", lambda o, n: (created.discard(o), created.add(n)))


@pytest.fixture
def registry():
    r = ProviderRegistry()
    register_builtin_providers(r)
    return r


@pytest.fixture
def context_store(db_path):
    return SessionContextStore(db_path, use_cache=True)


@pytest.fixture
def session_manager(db_path, context_store):
    return SessionManager(db_path, context_store)


def test_create_session_default_provider(session_manager, registry):
    provider = registry.get("shell")
    assert provider is not None
    session_manager.create_session("api", provider)
    sessions = session_manager.list_sessions()
    assert len(sessions) == 1
    assert sessions[0]["session_name"] == "api"
    assert sessions[0]["provider_id"] == "shell"


def test_list_sessions(session_manager, registry):
    provider = registry.get("shell")
    session_manager.create_session("a", provider)
    session_manager.create_session("b", provider)
    sessions = session_manager.list_sessions()
    assert len(sessions) == 2
    names = [s["session_name"] for s in sessions]
    assert "a" in names and "b" in names


def test_use_and_current(context_store, session_manager, registry):
    provider = registry.get("shell")
    session_manager.create_session("api", provider)
    context_store.set_current_session(chat_id=100, session_name="api")
    assert context_store.get_current_session(100) == "api"
    context_store.set_current_session(100, None)
    assert context_store.get_current_session(100) is None


def test_rename_session(session_manager, context_store, registry):
    provider = registry.get("shell")
    session_manager.create_session("api", provider)
    context_store.set_current_session(200, "api")
    session_manager.rename_session("api", "backend")
    assert context_store.get_current_session(200) == "backend"
    meta = session_manager.get_session_metadata("backend")
    assert meta is not None
    assert session_manager.get_session_metadata("api") is None


def test_kill_session(session_manager, context_store, registry):
    provider = registry.get("shell")
    session_manager.create_session("api", provider)
    context_store.set_current_session(300, "api")
    session_manager.kill_session("api")
    assert session_manager.get_session_metadata("api") is None
    assert context_store.get_current_session(300) is None
