# Setup

## Python y pyenv

El proyecto usa **Python 3.11+**. Se recomienda [pyenv](https://github.com/pyenv/pyenv) para gestionar la versión.

**Dependencias de compilación (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

**Uso con pyenv (tras instalarlo y tenerlo en el PATH):**

```bash
pyenv install 3.12          # instalar Python 3.12
pyenv rehash                # actualizar shims
# En este repo, .python-version fija 3.12; al hacer cd aquí se usará automáticamente
python --version            # debe mostrar 3.12.x
```

Para usar una versión concreta solo en este proyecto: `pyenv local 3.12`. Para global: `pyenv global 3.12`.

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
