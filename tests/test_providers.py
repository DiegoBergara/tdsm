"""Tests for provider registry and built-in providers (availability, format_user_command)."""

import pytest

from tdsm.providers import (
    ProviderRegistry,
    register_builtin_providers,
    ShellProvider,
    ClaudeCodeProvider,
)


def test_registry_get_and_list():
    registry = ProviderRegistry()
    registry.register(ShellProvider())
    provider = registry.get("shell")
    assert provider is not None
    assert provider.id == "shell"
    assert provider.display_name == "Shell"


def test_shell_always_available():
    p = ShellProvider()
    assert p.is_available() is True


def test_shell_format_user_command():
    p = ShellProvider()
    assert p.format_user_command("ls -la") == "ls -la"


def test_shell_modes():
    p = ShellProvider()
    assert p.get_modes() == ["shell"]
    assert p.default_mode() == "shell"
    assert p.next_mode("shell") == "shell"


def test_builtin_providers_registered():
    registry = ProviderRegistry()
    register_builtin_providers(registry)
    ids = registry.list_ids()
    assert "shell" in ids
    assert "claude-code" in ids
    assert "codex" in ids
    assert "cursor-cli" in ids
    assert "gemini-cli" in ids


def test_registry_list_all_with_availability():
    registry = ProviderRegistry()
    register_builtin_providers(registry)
    pairs = registry.list_all()
    assert len(pairs) == 5
    for provider, available in pairs:
        if provider.id == "shell":
            assert available is True
