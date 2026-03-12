# Proposal: Telegram Dev Session Manager (TDSM) — Initial Implementation

## Why

Developers and teams need a way to manage persistent development sessions and run CLI-based coding assistants (Claude Code, Codex, Cursor CLI, Gemini CLI) from Telegram. Today this requires manual SSH, local terminals, or ad-hoc scripts. A dedicated bot that uses **tmux as the session backend** and exposes session creation, command execution, provider switching, and observability via Telegram fills that gap. Building it now as an open-source, self-hosted tool allows extensibility through a provider architecture and keeps the scope on CLI assistants only (no direct LLM APIs or IDE integrations in v1).

## What Changes

- **New codebase**: Python 3.11+ application using python-telegram-bot, SQLite, and tmux.
- **Session lifecycle**: Create named sessions with optional provider (`/new`), list sessions (`/list`), set current session per chat (`/use`), show current (`/current`), rename (`/rename`), kill (`/kill`).
- **Command execution**: Messages without `/` run in the current session; `/send <session> <command>` runs in another session without changing current.
- **Session control**: `/ctrlc` and optionally `/ctrlc <session>`, `/clear` and optionally `/clear <session>`.
- **Observability**: `/status [session]`, `/logs [session]`, `/history [session]` (history stored in SQLite).
- **Provider system**: Shared provider interface (availability, modes, bootstrap, command formatting), registry, `/providers` command, and built-in providers: shell, claude-code, codex, cursor-cli, gemini-cli (support can be shallow initially).
- **Assistant modes**: `/mode` (cycle), `/mode <mode>` (set), `/modes` (list); modes are provider-specific.
- **Persistence**: SQLite for managed_sessions, chat_context (current session per chat), and command_history.
- **Security**: Access restricted via `ALLOWED_USER_IDS`; only allowlisted users may execute commands.
- **Project structure**: Repository layout per PRD (src/tdsm, tests, docs, Docker, CI, pyproject.toml).

No breaking changes (greenfield).

## Capabilities

### New Capabilities

- `sessions`: Session lifecycle — create, list, select current, show current, rename, kill; current session per chat.
- `execution`: Run command in current session; send command to another session via `/send`.
- `control`: Interrupt (Ctrl+C) and clear terminal; optional session argument.
- `observability`: Session status, last output; logs (last N lines); command history from SQLite.
- `providers`: Provider interface, registry, `/providers` list, built-in providers (shell, claude-code, codex, cursor-cli, gemini-cli).
- `modes`: Cycle/set/list assistant modes; provider-specific mode support.
- `persistence`: SQLite schema (managed_sessions, chat_context, command_history) and history store.
- `auth`: User allowlist via `ALLOWED_USER_IDS`; reject non-allowlisted users.
- `bot-setup`: Bot commands list, BotFather setup instructions, env vars and docs.

### Modified Capabilities

- _(None — new project.)_

## Impact

- **New repo layout**: `src/tdsm/` (bot, config, auth, command_router, session_manager, session_context, history_store, tmux_controller, providers/, handlers/), `tests/`, `docs/`, `pyproject.toml`, Dockerfile, docker-compose, CI workflow.
- **Dependencies**: python-telegram-bot, SQLite (stdlib), subprocess; optional pydantic; tooling: pytest, ruff, black, mypy (optional).
- **External**: Requires Telegram Bot Token and tmux on the host (or container). No direct LLM APIs.
- **Operational**: Self-hosted; operators must set `TELEGRAM_BOT_TOKEN`, `ALLOWED_USER_IDS`, and optionally `DATABASE_PATH`, `LOG_LEVEL`, `DEFAULT_LOG_LINES`.
