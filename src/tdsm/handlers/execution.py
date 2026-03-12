"""Execution handler: run command in current session; /send <session> <command>. Records in history."""

from telegram import Update
from telegram.ext import ContextTypes

from tdsm import tmux_controller
from tdsm.session_context import SessionContextStore
from tdsm.session_manager import SessionManager
from tdsm.history_store import HistoryStore
from tdsm.providers.registry import ProviderRegistry
from tdsm.update_utils import get_command_text
from tdsm.handlers import observability


def _manager(context: ContextTypes.DEFAULT_TYPE) -> SessionManager:
    return context.bot_data["session_manager"]


def _context_store(context: ContextTypes.DEFAULT_TYPE) -> SessionContextStore:
    return context.bot_data["session_context"]


def _history(context: ContextTypes.DEFAULT_TYPE) -> HistoryStore:
    return context.bot_data["history_store"]


def _registry(context: ContextTypes.DEFAULT_TYPE) -> ProviderRegistry:
    return context.bot_data["provider_registry"]


async def handle_message_as_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Run message text as command in current session. No / prefix."""
    if not update.message or not update.message.text or not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    command = update.message.text.strip()
    ctx = _context_store(context)
    current = ctx.get_current_session(chat_id)
    if not current:
        await update.message.reply_text("No current session. Use /use <name> or /new <name> [provider].")
        return
    manager = _manager(context)
    meta = manager.get_session_metadata(current)
    if not meta:
        await update.message.reply_text(f"Session '{current}' not found.")
        return
    provider = _registry(context).get(meta["provider_id"])
    if not provider:
        await update.message.reply_text(f"Provider {meta['provider_id']} not found.")
        return
    formatted = provider.format_user_command(command)
    tmux_controller.send_keys(current, formatted, enter=True)
    _history(context).append(chat_id, current, command)
    logs_text = observability.get_logs_text(context, current)
    await update.message.reply_text(logs_text or "Command sent.")


async def handle_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send command to another session: /send <session> <command>."""
    if not update.message or not update.effective_chat:
        return
    text = get_command_text(update, context)
    if not text:
        await update.message.reply_text("Usage: /send <session> <command>")
        return
    parts = text.split(maxsplit=2)
    if len(parts) < 3:
        await update.message.reply_text("Usage: /send <session> <command>")
        return
    session_name = parts[1].strip()
    command = parts[2].strip()
    manager = _manager(context)
    if not manager.get_session_metadata(session_name):
        await update.message.reply_text(f"Session not found: {session_name}")
        return
    meta = manager.get_session_metadata(session_name)
    provider = _registry(context).get(meta["provider_id"]) if meta else None
    formatted = provider.format_user_command(command) if provider else command
    tmux_controller.send_keys(session_name, formatted, enter=True)
    _history(context).append(update.effective_chat.id, session_name, command)
    logs_text = observability.get_logs_text(context, session_name)
    await update.message.reply_text(logs_text or f"Command sent to {session_name}.")
