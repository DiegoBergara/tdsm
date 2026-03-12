"""Claude Code provider. Shallow: availability check (claude in PATH), modes, format_user_command."""

import shutil

from tdsm.providers.base import BaseProvider


class ClaudeCodeProvider(BaseProvider):
    """Claude Code CLI assistant."""

    @property
    def id(self) -> str:
        return "claude-code"

    @property
    def display_name(self) -> str:
        return "Claude Code"

    def is_available(self) -> bool:
        return shutil.which("claude") is not None

    def get_modes(self) -> list[str]:
        return ["chat", "edit", "review", "diff", "plan", "apply"]

    def default_mode(self) -> str:
        return "chat"

    def next_mode(self, current_mode: str) -> str:
        modes = self.get_modes()
        try:
            i = modes.index(current_mode)
            return modes[(i + 1) % len(modes)]
        except ValueError:
            return modes[0]

    def bootstrap_commands(self) -> list[str]:
        return ["claude"]

    def format_user_command(self, command: str) -> str:
        return command
