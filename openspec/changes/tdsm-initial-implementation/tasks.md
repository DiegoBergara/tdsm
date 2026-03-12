# Tasks: TDSM Initial Implementation

## 1. Project setup

- [x] 1.1 Create repository structure (src/tdsm/, tests/, docs/, .github/workflows/)
- [x] 1.2 Add pyproject.toml with Python 3.11+, python-telegram-bot, and dev deps (pytest, ruff, black)
- [x] 1.3 Add config module reading TELEGRAM_BOT_TOKEN, ALLOWED_USER_IDS, DATABASE_PATH, LOG_LEVEL, DEFAULT_LOG_LINES; fail fast on missing required vars

## 2. Auth

- [x] 2.1 Implement auth layer: allowlist check using ALLOWED_USER_IDS before routing; reject non-allowlisted users with clear response

## 3. Persistence

- [x] 3.1 Define and create SQLite schema: managed_sessions, chat_context, command_history (per PRD)
- [x] 3.2 Implement session context store (get/set current session per chat_id; persist to chat_context; optional in-memory cache)
- [x] 3.3 Implement history_store: append command (chat_id, session_name, command, timestamp) and query last N per session

## 4. Tmux controller

- [x] 4.1 Implement TmuxController: create session, send keys (including Ctrl+C), capture pane output (last N lines), kill session, clear (send clear command)
- [x] 4.2 Add abstraction so handlers never call tmux CLI directly; document max output size / truncation for Telegram

## 5. Providers

- [x] 5.1 Define BaseProvider interface (id, display_name, is_available, get_modes, default_mode, next_mode, bootstrap_commands, format_user_command)
- [x] 5.2 Implement provider registry: register providers, get by id, list all with availability
- [x] 5.3 Implement shell provider (always available, single mode "shell", pass-through format_user_command)
- [x] 5.4 Implement claude-code provider (shallow: availability check, modes, format_user_command)
- [x] 5.5 Implement codex provider (shallow)
- [x] 5.6 Implement cursor-cli provider (shallow)
- [x] 5.7 Implement gemini-cli provider (shallow)
- [x] 5.8 Wire built-in providers into registry at startup

## 6. Session manager

- [x] 6.1 Implement session manager: create session (tmux + provider + persist to managed_sessions), list sessions, get session metadata, rename (tmux + DB), kill (tmux + DB)
- [x] 6.2 Integrate session manager with session context store (set current on /use; update on rename/kill if current affected)
- [x] 6.3 On session create: run provider bootstrap_commands in tmux if any; set initial mode from provider default_mode

## 7. Handlers

- [x] 7.1 Sessions handler: /new, /list, /use, /current, /rename, /kill (delegate to session manager and context store)
- [x] 7.2 Execution handler: run message-as-command in current session (provider.format_user_command + tmux send); /send <session> <command> to specific session; record command in history_store
- [x] 7.3 Control handler: /ctrlc [session], /clear [session] via TmuxController
- [x] 7.4 Observability handler: /status [session], /logs [session], /history [session] (use DEFAULT_LOG_LINES for logs)
- [x] 7.5 Providers handler: /providers (list from registry with availability)
- [x] 7.6 Modes handler: /mode (cycle), /mode <mode> (set), /modes (list); persist mode in session metadata and use provider next_mode/default_mode

## 8. Bot entry and routing

- [ ] 8.1 Implement command router: parse command/prefix and dispatch to correct handler (auth already applied)
- [ ] 8.2 Wire bot entry point: load config, init DB and schema, init registry and providers, register handlers with router, start polling
- [ ] 8.3 Add /help that lists commands (per bot-setup spec)

## 9. Docs and ops

- [ ] 9.1 Add .env.example with TELEGRAM_BOT_TOKEN, ALLOWED_USER_IDS, DATABASE_PATH, LOG_LEVEL, DEFAULT_LOG_LINES and short descriptions
- [ ] 9.2 Document BotFather setup and /setcommands payload (help, providers, new, list, use, current, send, status, logs, history, mode, modes, ctrlc, kill, rename, clear)
- [ ] 9.3 Add docs: architecture.md, commands.md, providers.md, security.md (per PRD)
- [ ] 9.4 Add Dockerfile and docker-compose.yml with persistent data volume for DATABASE_PATH
- [ ] 9.5 Add GitHub Actions CI: lint (ruff, black), tests (pytest); mock tmux in tests
- [ ] 9.6 Add README with install, env, run, and link to BotFather and docs

## 10. Tests

- [ ] 10.1 Tests for session creation, list, use, current, rename, kill (mock tmux and DB)
- [ ] 10.2 Tests for provider registry and built-in providers (availability, format_user_command)
- [ ] 10.3 Tests for command parsing and routing (auth allowlist, handler dispatch)
- [ ] 10.4 Tests for history_store append and query
- [ ] 10.5 Tests for session context get/set and persistence
