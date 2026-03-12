"""Shell provider: always available, single mode 'shell', pass-through format_user_command."""

from tdsm.providers.base import BaseProvider


class ShellProvider(BaseProvider):
    """Plain shell - no assistant. Always available in tmux."""

    @property
    def id(self) -> str:
        return "shell"

    @property
    def display_name(self) -> str:
        return "Shell"

    def is_available(self) -> bool:
        return True

    def get_modes(self) -> list[str]:
        return ["shell"]

    def default_mode(self) -> str:
        return "shell"

    def next_mode(self, current_mode: str) -> str:
        return "shell"

    def bootstrap_commands(self) -> list[str]:
        return []

    def format_user_command(self, command: str) -> str:
        return command
