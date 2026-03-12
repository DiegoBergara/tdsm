# Architecture

TDSM is a single-process Telegram bot that manages persistent development sessions backed by tmux and supports CLI coding assistants through a provider abstraction.

## High-Level Flow

```
Telegram Bot API
       |
       v
 Bot Application
       |
       +-- Authorization Layer (allowlist)
       +-- Command Router
       +-- Session Context Store
       +-- Session Manager
       +-- Provider Registry
       +-- Provider Adapters
       +-- History Store (SQLite)
       +-- Tmux Controller
             |
             v
           tmux
             |
             v
      Managed Sessions
```

## Components

- **Authorization**: Only users whose Telegram user ID is in `ALLOWED_USER_IDS` can use the bot. Check is done in the command router before any handler runs.
- **Command Router**: Parses incoming messages (commands vs plain text), applies auth, and dispatches to the appropriate handler (sessions, execution, control, observability, providers, modes).
- **Session Context Store**: Persists and caches the "current session" per chat (SQLite `chat_context` + in-memory cache).
- **Session Manager**: Creates, lists, renames, and kills tmux sessions; persists metadata in `managed_sessions`; runs provider bootstrap commands on create; updates session context on rename/kill.
- **Provider Registry**: Holds all providers (shell, claude-code, codex, cursor-cli, gemini-cli). Handlers query by id and use for availability, modes, and command formatting.
- **History Store**: Appends each executed command to `command_history` and supports querying by session.
- **Tmux Controller**: Single abstraction over the tmux CLI (create session, send keys, capture pane, kill, clear). Handlers never call tmux directly.

## Data Flow

- **Create session**: Router → sessions handler → session manager (tmux create + bootstrap + DB insert).
- **Run command**: Router → execution handler → provider.format_user_command → tmux send_keys → history_store.append.
- **Status/Logs**: Router → observability handler → session manager (metadata) + tmux_controller.capture_pane.

## Technology

- Python 3.11+, python-telegram-bot, SQLite (stdlib), subprocess for tmux. No direct LLM APIs; only CLI assistants via providers.
