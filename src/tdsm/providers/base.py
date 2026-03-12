"""Base provider interface. All providers must implement this interface."""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Shared interface for CLI assistant providers."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier (e.g. 'shell', 'claude-code')."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name for /providers list."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this provider can be used (e.g. binary in PATH)."""
        ...

    @abstractmethod
    def get_modes(self) -> list[str]:
        """Return list of supported assistant modes."""
        ...

    @abstractmethod
    def default_mode(self) -> str:
        """Return the default mode when creating a session."""
        ...

    @abstractmethod
    def next_mode(self, current_mode: str) -> str:
        """Return the next mode when cycling (e.g. /mode with no args)."""
        ...

    @abstractmethod
    def bootstrap_commands(self) -> list[str]:
        """Commands to run in tmux when session is created (e.g. start assistant). May be empty."""
        ...

    @abstractmethod
    def format_user_command(self, command: str) -> str:
        """Format user text as the command to send to the session (provider-specific)."""
        ...
