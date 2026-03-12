"""Sessions handler: /new, /list, /use, /current, /rename, /kill. Auth is done before routing."""

from telegram import Update
from telegram.ext import ContextTypes

from tdsm.session_context import SessionContextStore
from tdsm.session_manager import SessionManager
from tdsm.providers.registry import ProviderRegistry
from tdsm.update_utils import get_command_text


def _manager(context: ContextTypes.DEFAULT_TYPE) -> SessionManager:
    return context.bot_data["session_manager"]


def _context_store(context: ContextTypes.DEFAULT_TYPE) -> SessionContextStore:
    return context.bot_data["session_context"]


def _registry(context: ContextTypes.DEFAULT_TYPE) -> ProviderRegistry:
    return context.bot_data["provider_registry"]


async def handle_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create session: /new <name> [provider]. Default provider: shell."""
    text = get_command_text(update, context)
    if not update.message or not text:
        await update.message.reply_text("Usage: /new <name> [provider]")
        return
    parts = text.split()
    if len(parts) < 2:
        await update.message.reply_text("Usage: /new <name> [provider]")
        return
    name = parts[1].strip()
    provider_id = parts[2].strip() if len(parts) > 2 else "shell"
    registry = _registry(context)
    provider = registry.get(provider_id)
    if not provider:
        await update.message.reply_text(f"Unknown provider: {provider_id}. Use /providers to list.")
        return
    if not provider.is_available():
        await update.message.reply_text(f"Provider {provider_id} is not available.")
        return
    manager = _manager(context)
    try:
        manager.create_session(name, provider)
        await update.message.reply_text(f"Session '{name}' created with provider {provider_id}.")
    except ValueError as e:
        await update.message.reply_text(str(e))


async def handle_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List sessions: /list. Mark current for this chat."""
    if not update.message or not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    manager = _manager(context)
    ctx = _context_store(context)
    current = ctx.get_current_session(chat_id)
    sessions = manager.list_sessions()
    lines = ["Sessions:"]
    for s in sessions:
        mark = " (current)" if s["session_name"] == current else ""
        lines.append(f"- {s['session_name']} [{s['provider_id']}]{mark}")
    await update.message.reply_text("\n".join(lines) if lines else "No sessions.")


async def handle_use(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set current session: /use <name>."""
    if not update.message or not update.effective_chat:
        return
    text = get_command_text(update, context)
    if not text:
        await update.message.reply_text("Usage: /use <name>")
        return
    parts = text.split()
    if len(parts) < 2:
        await update.message.reply_text("Usage: /use <name>")
        return
    name = parts[1].strip()
    manager = _manager(context)
    if not manager.get_session_metadata(name):
        await update.message.reply_text(f"Session not found: {name}")
        return
    _context_store(context).set_current_session(update.effective_chat.id, name)
    await update.message.reply_text(f"Current session: {name}")


async def handle_current(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current session: /current."""
    if not update.message or not update.effective_chat:
        return
    current = _context_store(context).get_current_session(update.effective_chat.id)
    if current:
        await update.message.reply_text(f"Current session: {current}")
    else:
        await update.message.reply_text("No current session. Use /use <name> or /new <name> [provider].")


async def handle_rename(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Rename session: /rename <old> <new>."""
    if not update.message:
        return
    text = get_command_text(update, context)
    if not text:
        await update.message.reply_text("Usage: /rename <old> <new>")
        return
    parts = text.split(maxsplit=2)
    if len(parts) < 3:
        await update.message.reply_text("Usage: /rename <old> <new>")
        return
    old_name, new_name = parts[1].strip(), parts[2].strip()
    manager = _manager(context)
    try:
        manager.rename_session(old_name, new_name)
        await update.message.reply_text(f"Renamed '{old_name}' to '{new_name}'.")
    except ValueError as e:
        await update.message.reply_text(str(e))


async def handle_kill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kill session: /kill <session>."""
    if not update.message:
        return
    text = get_command_text(update, context)
    if not text:
        await update.message.reply_text("Usage: /kill <session>")
        return
    parts = text.split()
    if len(parts) < 2:
        await update.message.reply_text("Usage: /kill <session>")
        return
    name = parts[1].strip()
    manager = _manager(context)
    try:
        manager.kill_session(name)
        await update.message.reply_text(f"Session '{name}' killed.")
    except ValueError as e:
        await update.message.reply_text(str(e))
