"""Control handler: /ctrlc [session], /clear [session] via TmuxController."""

from telegram import Update
from telegram.ext import ContextTypes

from tdsm import tmux_controller
from tdsm.session_context import SessionContextStore
from tdsm.session_manager import SessionManager
from tdsm.update_utils import get_command_text


def _manager(context: ContextTypes.DEFAULT_TYPE) -> SessionManager:
    return context.bot_data["session_manager"]


def _context_store(context: ContextTypes.DEFAULT_TYPE) -> SessionContextStore:
    return context.bot_data["session_context"]


async def handle_ctrlc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send Ctrl+C: /ctrlc or /ctrlc <session>."""
    if not update.message or not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    text = get_command_text(update, context)
    parts = text.split() if text else []
    if len(parts) >= 2:
        session_name = parts[1].strip()
    else:
        session_name = _context_store(context).get_current_session(chat_id)
    if not session_name:
        await update.message.reply_text("No current session. Use /use <name> or specify session: /ctrlc <session>")
        return
    if not _manager(context).get_session_metadata(session_name):
        await update.message.reply_text(f"Session not found: {session_name}")
        return
    tmux_controller.send_ctrl_c(session_name)
    await update.message.reply_text(f"Ctrl+C sent to {session_name}.")


async def handle_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear terminal: /clear or /clear <session>."""
    if not update.message or not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    text = get_command_text(update, context)
    parts = text.split() if text else []
    if len(parts) >= 2:
        session_name = parts[1].strip()
    else:
        session_name = _context_store(context).get_current_session(chat_id)
    if not session_name:
        await update.message.reply_text("No current session. Use /use <name> or specify session: /clear <session>")
        return
    if not _manager(context).get_session_metadata(session_name):
        await update.message.reply_text(f"Session not found: {session_name}")
        return
    tmux_controller.clear_pane(session_name)
    await update.message.reply_text(f"Cleared {session_name}.")
