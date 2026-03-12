# Design: TDSM Initial Implementation

## Context

TDSM is a new Python application: a Telegram bot that manages persistent development sessions backed by tmux and supports CLI coding assistants (Claude Code, Codex, Cursor CLI, Gemini CLI) through a provider abstraction. There is no existing codebase; this design establishes the initial architecture. Stakeholders are developers and operators who self-host the bot. Constraints: Python 3.11+, python-telegram-bot, SQLite, tmux on the host; no direct LLM APIs or IDE integrations in v1.

## Goals / Non-Goals

**Goals:**

- Single-process bot with clear separation: auth, command routing, session context, session manager, provider registry, tmux controller, history store.
- Provider interface and registry so new CLI tools can be added without changing core logic.
- One current session per Telegram chat; commands without `/` run in that session.
- Persistence of sessions, chat→current-session mapping, and command history in SQLite.
- Allowlist-based auth via `ALLOWED_USER_IDS`.
- Documented setup (BotFather, env vars), Docker support, and CI.

**Non-Goals:**

- IDE integrations, direct LLM APIs, Kubernetes, multi-host orchestration, web UI, SSH cluster management.
- Live log streaming, port detection, or advanced observability in v1.

## Decisions

### 1. Layered architecture (Bot → Router → Handlers → Manager → Tmux)

**Choice:** Request flow: Telegram update → auth check → command router → handler (sessions, execution, control, observability, providers) → session manager / tmux controller / history store as needed.

**Rationale:** Keeps routing and parsing in one place; handlers stay thin and delegate to domain modules. Alternatives: single monolithic handler (hard to extend), or event bus (overkill for v1).

### 2. Session context in SQLite + in-memory cache

**Choice:** `chat_context` table stores `(chat_id, current_session)`. On startup, optionally load into a small in-memory cache keyed by `chat_id` for fast lookup; writes go to DB (and cache) so state survives restarts.

**Rationale:** SQLite matches PRD and keeps deployment simple. In-memory cache avoids a DB round-trip on every message. Alternative: DB-only (simpler but slower).

### 3. Tmux controller as single abstraction over tmux

**Choice:** One `TmuxController` (or equivalent) that wraps subprocess calls to `tmux`: create session, send keys, capture output, kill session, etc. Session manager and execution handlers call this layer only.

**Rationale:** Isolates tmux CLI usage and makes mocking easy in tests. Alternative: inline subprocess calls in handlers (harder to test and change).

### 4. Provider interface: abstract base + registry

**Choice:** `BaseProvider` (or protocol) with `id`, `display_name`, `is_available()`, `get_modes()`, `default_mode()`, `next_mode(current)`, `bootstrap_commands()`, `format_user_command(command)`. Registry holds provider instances; handlers ask registry for list and for provider by id.

**Rationale:** Matches PRD and allows shallow implementations per provider (e.g., shell always available; others may check PATH). Alternative: hardcoded if/else (not extensible).

### 5. History store interface

**Choice:** Dedicated module (e.g. `history_store`) that inserts into `command_history` and exposes “last N for session” (and optionally by chat). Session manager / execution handler records each executed command.

**Rationale:** Centralizes schema and query logic; keeps handlers free of SQL. Alternative: handlers write directly to DB (scattered persistence logic).

### 6. Config via env and single config module

**Choice:** All env vars (`TELEGRAM_BOT_TOKEN`, `ALLOWED_USER_IDS`, `DATABASE_PATH`, `LOG_LEVEL`, `DEFAULT_LOG_LINES`) read in a `config` module (or Pydantic settings) at startup; invalid or missing required values fail fast.

**Rationale:** No config files to deploy; fits Docker and 12-factor style. Alternative: config file (adds another artifact and env vs file precedence issues).

### 7. No async in tmux layer initially

**Choice:** Tmux controller uses blocking subprocess (e.g. `subprocess.run` or `Popen` + communicate) so as not to block the event loop, run tmux in a thread pool or keep runs short and accept blocking.

**Rationale:** python-telegram-bot can use thread-based or asyncio; tmux CLI is blocking. Running tmux in executor or keeping commands short avoids blocking the bot. Alternative: full asyncio subprocess (more complex, same underlying blocking I/O for tmux).

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Tmux output capture truncation or buffering | Define max output size and document; use `tmux capture-pane` with `-p` and limit lines; truncate in response with “… (truncated)” |
| Long-running command blocks bot response | Run tmux send in executor; return “Command sent” immediately; user uses /status or /logs to see output |
| Provider “available” check is slow or flaky | Cache `is_available()` per process lifecycle or with TTL; document that /providers may be stale |
| SQLite under concurrent writes | Single process and serialized handler execution (Telegram updates) keep contention low; use WAL if needed |
| Allowlist bypass if chat_id is spoofed | Rely on Telegram’s update authenticity; validate that update comes from Telegram (bot library does this); document that ALLOWED_USER_IDS is the only access control |

## Migration Plan

- **Deploy:** New install: set env vars, run migrations (or create DB and tables from schema), start bot. Docker: mount volume for `DATABASE_PATH`, run container with env.
- **Rollback:** Stop bot; no backward compatibility needed for v1. DB schema is additive for future changes.
- **Data:** No migration from existing system. For future schema changes, add migration scripts or versioned schema in repo.

## Open Questions

- Whether to use python-telegram-bot’s async (PTB v20+) or legacy sync API: decide based on team preference and whether other async I/O is planned; both can work with a thread pool for tmux.
- Exact tmux capture strategy (e.g. `capture-pane -p -S -N`) and line limit for /logs and /status to avoid hitting Telegram message size limits.
- Whether to add a simple “max command length” or rate limit per chat to reduce abuse surface; can be deferred to a follow-up.
