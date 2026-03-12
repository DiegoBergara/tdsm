# PRD — Telegram Dev Session Manager (TDSM)

## 1. Product Overview

Telegram Dev Session Manager (TDSM) is an open-source Telegram bot designed to manage persistent development sessions and CLI-based coding assistants through Telegram.

The system uses **tmux as the session backend** and allows users to:

* create and manage persistent development sessions
* run shell commands remotely
* integrate with CLI coding assistants such as:
  * Claude Code
  * Codex CLI
  * Cursor CLI
  * Gemini CLI
* switch assistant modes
* inspect logs and session status
* interrupt processes
* maintain command history

The architecture must support **extensible providers**, allowing new CLI tools to be integrated without modifying core logic.

---

# 2. Goals

### Primary Goals

1. Manage persistent development sessions through Telegram
2. Execute commands remotely in tmux sessions
3. Support CLI coding assistants via provider architecture
4. Allow switching assistant modes
5. Maintain session logs and history
6. Provide a simple conversational workflow

### Secondary Goals

1. Be easy to install and self-host
2. Be easy to extend with new providers
3. Provide strong documentation
4. Maintain open-source code quality

---

# 3. Non-Goals

Out of scope for v1:

* IDE integrations
* direct LLM API integrations
* container orchestration
* Kubernetes support
* distributed multi-host management
* web interface
* SSH cluster management

The project integrates **CLI assistants only**, not direct APIs.

---

# 4. Target Users

* software engineers
* DevOps engineers
* backend developers
* homelab operators
* AI coding assistant users

---

# 5. Core Concepts

## Managed Session

A managed session is a persistent tmux session associated with:

* session name
* provider type
* assistant mode
* working directory
* metadata

Example:

```
api [shell]
refactor [claude-code]
review [codex]
frontend [cursor-cli]
```

---

## Current Session

Each Telegram chat maintains a **current active session**.

Commands sent without `/` are executed in the current session.

Example:

```
/use api
npm run dev
```

---

## Provider

A provider represents a CLI development tool.

Providers encapsulate logic required to interact with that CLI.

Examples:

* shell
* claude-code
* codex
* cursor-cli
* gemini-cli

Providers must be implemented behind a shared interface.

---

## Assistant Mode

Some assistants support multiple operational modes.

Examples:

```
chat
edit
review
diff
plan
apply
```

Modes are **provider specific**.

The system must support switching modes generically.

---

# 6. High-Level Architecture

```
Telegram Bot API
       |
       v
 Bot Application
       |
       +-- Authorization Layer
       +-- Command Router
       +-- Session Context Store
       +-- Session Manager
       +-- Provider Registry
       +-- Provider Adapters
       +-- History Store (SQLite)
       +-- tmux Controller
             |
             v
           tmux
             |
             v
      Managed Sessions
```

---

# 7. Technology Stack

Language:

Python 3.11+

Libraries:

* python-telegram-bot
* SQLite
* subprocess
* pydantic (optional)

Tooling:

* tmux
* pytest
* ruff
* black
* mypy (optional)

Packaging:

* pyproject.toml

---

# 8. Functional Requirements

## Session Commands

### Create Session

```
/new <name> [provider]
```

Example:

```
/new api shell
/new refactor claude-code
```

Default provider: `shell`.

---

### List Sessions

```
/list
```

Example response:

```
Sessions:
- api [shell] (current)
- refactor [claude-code]
- review [codex]
```

---

### Select Session

```
/use <name>
```

Sets the current session.

---

### Show Current Session

```
/current
```

Example:

```
Current session: api
```

---

## Command Execution

### Run Command

Any message not starting with `/`.

Example:

```
npm run dev
```

Executes in the current session.

---

### Send Command to Another Session

```
/send <session> <command>
```

Example:

```
/send frontend pnpm dev
```

Current session remains unchanged.

---

## Session Control

### Interrupt Process

```
/ctrlc [session]
```

Sends Ctrl+C.

---

### Kill Session

```
/kill <session>
```

Terminates session.

---

### Rename Session

```
/rename <old> <new>
```

---

### Clear Terminal

```
/clear [session]
```

---

# 9. Observability

### Session Status

```
/status [session]
```

Returns:

```
Session: api
Provider: shell
Mode: shell

Last output:
Server running on port 3000
```

---

### Logs

```
/logs [session]
```

Returns last N lines.

---

### Command History

```
/history [session]
```

Stored in SQLite.

---

# 10. Provider Commands

### List Providers

```
/providers
```

Example:

```
Providers:
- shell (available)
- claude-code (available)
- codex (unavailable)
- cursor-cli (available)
- gemini-cli (available)
```

---

# 11. Assistant Mode Commands

### Cycle Mode

```
/mode
```

Cycles to next mode.

Example:

```
Session: refactor
Provider: claude-code
Mode: edit
```

---

### Set Mode

```
/mode <mode>
```

Example:

```
/mode review
```

---

### List Modes

```
/modes
```

Example:

```
Available modes:
chat
edit
review
```

---

# 12. Provider Interface

Providers must implement a shared interface.

Example concept:

```python
class BaseProvider:

    id: str
    display_name: str

    def is_available(self) -> bool: ...

    def get_modes(self) -> list[str]: ...

    def default_mode(self) -> str: ...

    def next_mode(self, current_mode: str) -> str: ...

    def bootstrap_commands(self) -> list[str]: ...

    def format_user_command(self, command: str) -> str: ...
```

---

# 13. Built-in Providers

v1 must include:

* shell
* claude-code
* codex
* cursor-cli
* gemini-cli

Provider support can initially be shallow.

---

# 14. Persistence

Database: SQLite

### Managed Sessions

```
managed_sessions
- session_name TEXT PRIMARY KEY
- provider_id TEXT
- mode TEXT
- working_directory TEXT
- created_at TEXT
- updated_at TEXT
```

### Chat Context

```
chat_context
- chat_id INTEGER
- current_session TEXT
```

### Command History

```
command_history
- id INTEGER
- chat_id INTEGER
- session_name TEXT
- command TEXT
- timestamp
```

---

# 15. Security

The bot must restrict access.

Environment variable:

```
ALLOWED_USER_IDS
```

Only allowlisted users may execute commands.

---

# 16. Environment Variables

`.env.example`

```
TELEGRAM_BOT_TOKEN=
ALLOWED_USER_IDS=
DATABASE_PATH=./data/tdsm.db
LOG_LEVEL=INFO
DEFAULT_LOG_LINES=50
```

---

# 17. Repository Structure

```
telegram-dev-session-manager
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
├── pyproject.toml
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── docs
│   ├── architecture.md
│   ├── commands.md
│   ├── providers.md
│   └── security.md
├── src
│   └── tdsm
│       ├── bot.py
│       ├── config.py
│       ├── auth.py
│       ├── command_router.py
│       ├── session_manager.py
│       ├── session_context.py
│       ├── history_store.py
│       ├── tmux_controller.py
│       ├── providers
│       │   ├── base.py
│       │   ├── registry.py
│       │   ├── shell.py
│       │   ├── claude_code.py
│       │   ├── codex.py
│       │   ├── cursor_cli.py
│       │   └── gemini_cli.py
│       └── handlers
│           ├── sessions.py
│           ├── execution.py
│           ├── observability.py
│           └── providers.py
├── tests
│   ├── test_sessions.py
│   ├── test_providers.py
│   ├── test_commands.py
│   └── test_history.py
└── .github/workflows/ci.yml
```

---

# 18. BotFather Setup

In Telegram open:

```
@BotFather
```

Create bot:

```
/newbot
```

Copy token.

---

## Set Bot Commands

Run:

```
/setcommands
```

Paste:

```
help - Show help
providers - List providers
new - Create session
list - List sessions
use - Select session
current - Show current session
send - Send command to another session
status - Show session status
logs - Show session logs
history - Show command history
mode - Switch assistant mode
modes - List provider modes
ctrlc - Send Ctrl+C
kill - Kill session
rename - Rename session
clear - Clear terminal
```

---

# 19. Testing Requirements

Use pytest.

Test:

* session creation
* provider registry
* command parsing
* session routing
* history persistence

Mock tmux.

---

# 20. Code Quality

Project must include:

* ruff
* black
* pytest
* GitHub Actions CI
* type hints

---

# 21. Docker Support

Include:

Dockerfile

docker-compose.yml

Mount persistent data directory.

---

# 22. Documentation

docs must include:

* architecture
* commands
* providers
* security

---

# 23. Future Enhancements

Possible future features:

* live log streaming
* port detection
* automatic server detection
* restart command
* SSH providers
* multi-host orchestration
* notification triggers
* assistant result parsing

---

# 24. Success Criteria

A user can:

1. create sessions
2. attach providers
3. run commands
4. switch modes
5. inspect logs
6. interrupt processes
7. send commands across sessions

all through Telegram.

---

# 25. Codex Build Instructions

Append to prompt:

```
Build this as a production-quality open source Python project.

Requirements:
- Python 3.11+
- python-telegram-bot
- tmux session backend
- provider-based architecture
- built-in providers for shell, claude-code, codex, cursor-cli, gemini-cli
- assistant modes
- SQLite persistence
- full README
- BotFather setup instructions
- CI pipeline
- Docker support
- tests with pytest
- modular architecture
- extensible provider registry
```

---
