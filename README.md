# TDSM (Telegram Dev Session Manager)

Telegram Dev Session Manager (TDSM) is an open-source Telegram bot that manages persistent development sessions and CLI-based coding assistants through Telegram. Sessions are backed by **tmux**; you can run shell commands, attach providers (e.g. Claude Code, Codex, Cursor CLI, Gemini CLI), switch modes, and inspect logs and history.

## Requirements

- Python 3.11+
- [tmux](https://github.com/tmux/tmux)
- A Telegram Bot Token ([BotFather](https://t.me/BotFather))

## Install

```bash
git clone <repo>
cd tdsm
pip install -e .
```

For development (lint + tests):

```bash
pip install -e ".[dev]"
```

## Configure

Copy `.env.example` to `.env` and set:

- **TELEGRAM_BOT_TOKEN** – from [@BotFather](https://t.me/BotFather) (`/newbot`)
- **ALLOWED_USER_IDS** – comma-separated Telegram user IDs (e.g. `123456789`)

Optional: `DATABASE_PATH`, `LOG_LEVEL`, `DEFAULT_LOG_LINES`. See [docs/setup.md](docs/setup.md) and [.env.example](.env.example).

## Run

```bash
export TELEGRAM_BOT_TOKEN=...
export ALLOWED_USER_IDS=...
tdsm
```

Or with Docker:

```bash
export TELEGRAM_BOT_TOKEN=...
export ALLOWED_USER_IDS=...
docker compose up -d
```

Data is persisted in the volume `tdsm-data` (default path inside container: `/data/tdsm.db`).

## BotFather commands

So users see the command menu in Telegram, set the bot command list in BotFather (`/setcommands`). The full list is in [docs/setup.md](docs/setup.md).

## Documentation

- [Setup (BotFather, env)](docs/setup.md)
- [Architecture](docs/architecture.md)
- [Commands](docs/commands.md)
- [Providers](docs/providers.md)
- [Security](docs/security.md)

## License

MIT. See [LICENSE](LICENSE).
