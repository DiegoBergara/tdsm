# Setup

## BotFather

1. Open [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot` and follow the prompts (name and username).
3. Copy the token you receive and set it as `TELEGRAM_BOT_TOKEN` in your environment or `.env` file.
4. Set the bot command list so users see the command menu:
   - In BotFather, send `/setcommands`.
   - Select your bot.
   - Paste the following (one line per command):

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

## Environment variables

See `.env.example`. Required: `TELEGRAM_BOT_TOKEN`, `ALLOWED_USER_IDS`. Optional: `DATABASE_PATH`, `LOG_LEVEL`, `DEFAULT_LOG_LINES`.

## Run

```bash
pip install -e .
export TELEGRAM_BOT_TOKEN=...
export ALLOWED_USER_IDS=123456789
tdsm
```

Or with a `.env` file (use a loader such as `python-dotenv` or export variables manually).
