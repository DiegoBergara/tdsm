# Providers

Providers are CLI development tools that can be attached to a session. Each provider implements a common interface: identifier, display name, availability check, modes, default/next mode, bootstrap commands, and command formatting.

## Built-in providers

| Id | Display name | Availability |
|----|--------------|-------------|
| `shell` | Shell | Always available. |
| `claude-code` | Claude Code | `claude` in PATH. |
| `codex` | Codex | `codex` in PATH. |
| `cursor-cli` | Cursor CLI | `cursor` in PATH. |
| `gemini-cli` | Gemini CLI | `gemini` or `gemini-cli` in PATH. |

## Modes

Modes are provider-specific. Examples: `chat`, `edit`, `review`, `diff`, `plan`, `apply`. Use `/mode` to cycle and `/mode <mode>` to set. Use `/modes` to list modes for the current session's provider.

## Adding a provider

Implement the `BaseProvider` interface in `tdsm/providers/base.py` and register it in `register_builtin_providers` in `tdsm/providers/__init__.py`. The interface requires: `id`, `display_name`, `is_available()`, `get_modes()`, `default_mode()`, `next_mode(current)`, `bootstrap_commands()`, `format_user_command(command)`.
