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
download - Download file or folder (as ZIP)
upload - Upload file(s); use --extract for ZIP
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

### File transfer (download/upload)

Optional; only needed if you use `/download` or `/upload`:

- **FILE_TRANSFER_BASE_PATH** – Base directory allowed for transfers. If unset, the session’s working directory is used as the only allowed base (paths must stay under it). Set to a directory path (e.g. `/home/user/workspace`) to allow access under that tree.
- **FILE_DOWNLOAD_MAX_SIZE** – Max size in bytes for a single file download (default: 20971520 = 20 MiB).
- **FILE_UPLOAD_MAX_SIZE** – Max size in bytes per uploaded file (default: 20971520 = 20 MiB). Telegram bot API limit is 20 MB.
- **ZIP_MAX_SIZE** – Max size in bytes for generated or extracted ZIPs (default: 20971520 = 20 MiB).

Recommended: set `FILE_TRANSFER_BASE_PATH` to a dedicated workspace root in production to limit which paths users can read/write.

## Run

```bash
pip install -e .
export TELEGRAM_BOT_TOKEN=...
export ALLOWED_USER_IDS=123456789
tdsm
```

Or with a `.env` file (use a loader such as `python-dotenv` or export variables manually).

## Debugging (el bot no responde a /start o /new)

Si envías `/start` o `/new` y el bot no contesta:

1. **Ver los logs en la terminal**  
   Arranca el bot desde una terminal (no en segundo plano) para ver toda la salida:
   ```bash
   cd /ruta/al/tdsm
   export $(grep -v '^#' .env | xargs)   # cargar .env en el shell
   tdsm
   ```

2. **Activar logs detallados**  
   En `.env` pon:
   ```env
   LOG_LEVEL=DEBUG
   ```
   Así verás cada update que recibe el bot y posibles errores.

3. **Comprobar que tu usuario está permitido**  
   Tu *user ID* de Telegram debe estar en `ALLOWED_USER_IDS` (varios IDs separados por comas). Para saber tu ID: escribe a [@userinfobot](https://t.me/userinfobot) en Telegram y usa el número que te devuelve en `ALLOWED_USER_IDS`.

4. **Webhook**  
   Si el bot se usó antes con webhook, Telegram puede seguir enviando los updates ahí y el polling no recibe nada. Desde v0.1.0 el bot borra el webhook al arrancar (`delete_webhook`) para que el polling funcione en local. Si aun así no responde, puedes borrarlo a mano con la API de Telegram (por ejemplo con `curl` y tu token).

5. **Errores en handlers**  
   Si hay una excepción dentro de un comando, se registra en los logs y el bot puede enviarte "Error interno. Revisa los logs del bot (LOG_LEVEL=DEBUG)." Revisa el traceback en la terminal.
