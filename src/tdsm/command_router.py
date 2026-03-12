"""
Command router: parse command/prefix and dispatch to correct handler.
Auth is applied first; only allowlisted users reach handlers.
"""

from telegram import Update
from telegram.ext import ContextTypes

from tdsm.auth import check_access, AccessDenied
from tdsm.handlers import sessions, execution, control, observability, providers_handler, modes, file_transfer as file_transfer_handler

# Single source of truth for command list (used by /help and /start).
COMMANDS_LINES = [
    "help - Show this help",
    "providers - List providers",
    "new - Create session",
    "list - List sessions",
    "use - Select session",
    "current - Show current session",
    "send - Send command to another session",
    "download, dl - Download file or folder (as ZIP)",
    "upload - Upload file(s); use --extract for ZIP",
    "status - Session status",
    "logs - Session logs",
    "history - Command history",
    "mode - Switch assistant mode",
    "modes - List modes",
    "ctrlc - Send Ctrl+C",
    "kill - Kill session",
    "rename - Rename session",
    "clear - Clear terminal",
]


def get_commands_text() -> str:
    """Return the list of commands as a single string (header + lines)."""
    return "Commands:\n" + "\n".join(COMMANDS_LINES)


async def dispatch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check auth, then parse message and dispatch to the appropriate handler."""
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    config = context.bot_data.get("config")
    if not config:
        await update.message.reply_text("Bot not configured.")
        return
    try:
        check_access(user_id, config.allowed_user_ids)
    except AccessDenied as e:
        await update.message.reply_text(e.message)
        return
    text = (update.message.text or "").strip()
    # Handle messages with document (upload)
    if update.message.document:
        await file_transfer_handler.handle_document_message(update, context)
        return
    if not text:
        return
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        cmd = parts[0].lstrip("/").lower()
        # Normalize: /new_ session -> cmd "new" with rest
        rest = parts[1] if len(parts) > 1 else ""
        # Reconstruct message.text for handlers that parse it (e.g. /new name provider)
        update.message.text = f"/{cmd} {rest}".strip()
        if cmd == "new":
            await sessions.handle_new(update, context)
        elif cmd == "list":
            await sessions.handle_list(update, context)
        elif cmd == "use":
            await sessions.handle_use(update, context)
        elif cmd == "current":
            await sessions.handle_current(update, context)
        elif cmd == "rename":
            await sessions.handle_rename(update, context)
        elif cmd == "kill":
            await sessions.handle_kill(update, context)
        elif cmd == "send":
            await execution.handle_send(update, context)
        elif cmd == "ctrlc":
            await control.handle_ctrlc(update, context)
        elif cmd == "clear":
            await control.handle_clear(update, context)
        elif cmd == "status":
            await observability.handle_status(update, context)
        elif cmd == "logs":
            await observability.handle_logs(update, context)
        elif cmd == "history":
            await observability.handle_history(update, context)
        elif cmd == "providers":
            await providers_handler.handle_providers(update, context)
        elif cmd == "mode":
            await modes.handle_mode(update, context)
        elif cmd == "modes":
            await modes.handle_modes(update, context)
        elif cmd in ("download", "dl"):
            await file_transfer_handler.handle_download(update, context)
        elif cmd == "upload":
            await file_transfer_handler.handle_upload(update, context)
        elif cmd == "start":
            await handle_start(update, context)
        elif cmd == "help":
            await handle_help(update, context)
        else:
            await update.message.reply_text(f"Unknown command: /{cmd}. Use /help for a list.")
    else:
        await execution.handle_message_as_command(update, context)


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List commands: /help."""
    if not update.message:
        return
    await update.message.reply_text(get_commands_text())


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message on /start: purpose + list of commands."""
    if not update.message:
        return
    purpose = (
        "TDSM es un bot para gestionar sesiones de desarrollo (tmux), "
        "ejecutar comandos en remoto y usar asistentes CLI.\n\n"
    )
    await update.message.reply_text(purpose + get_commands_text())
