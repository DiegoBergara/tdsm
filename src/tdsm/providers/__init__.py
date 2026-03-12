"""Provider adapters for CLI assistants. Wire built-in providers into registry at startup."""

from tdsm.providers.base import BaseProvider
from tdsm.providers.registry import ProviderRegistry
from tdsm.providers.shell import ShellProvider
from tdsm.providers.claude_code import ClaudeCodeProvider
from tdsm.providers.codex import CodexProvider
from tdsm.providers.cursor_cli import CursorCliProvider
from tdsm.providers.gemini_cli import GeminiCliProvider

__all__ = [
    "BaseProvider",
    "ProviderRegistry",
    "ShellProvider",
    "ClaudeCodeProvider",
    "CodexProvider",
    "CursorCliProvider",
    "GeminiCliProvider",
    "register_builtin_providers",
]


def register_builtin_providers(registry: ProviderRegistry) -> None:
    """Register all built-in providers (shell, claude-code, codex, cursor-cli, gemini-cli)."""
    registry.register(ShellProvider())
    registry.register(ClaudeCodeProvider())
    registry.register(CodexProvider())
    registry.register(CursorCliProvider())
    registry.register(GeminiCliProvider())
