"""Observability handler: /status [session], /logs [session], /history [session]. Uses DEFAULT_LOG_LINES."""

from telegram import Update
from telegram.ext import ContextTypes

from tdsm import tmux_controller
from tdsm.session_context import SessionContextStore
from tdsm.session_manager import SessionManager
from tdsm.history_store import HistoryStore
from tdsm.update_utils import get_command_text


def _manager(context: ContextTypes.DEFAULT_TYPE) -> SessionManager:
    return context.bot_data["session_manager"]


def _context_store(context: ContextTypes.DEFAULT_TYPE) -> SessionContextStore:
    return context.bot_data["session_context"]


def _history(context: ContextTypes.DEFAULT_TYPE) -> HistoryStore:
    return context.bot_data["history_store"]


def _default_log_lines(context: ContextTypes.DEFAULT_TYPE) -> int:
    return context.bot_data["config"].default_log_lines


def get_logs_text(context: ContextTypes.DEFAULT_TYPE, session_name: str) -> str | None:
    """Build the same output as /logs for a given session. Returns None if session not found."""
    if not _manager(context).get_session_metadata(session_name):
        return None
    try:
        out = tmux_controller.capture_pane(session_name, lines=_default_log_lines(context))
        return out or "(empty)"
    except Exception as e:
        return f"Error: {e}"


def get_status_text(context: ContextTypes.DEFAULT_TYPE, session_name: str) -> str | None:
    """Build the same status message as /status for a given session. Returns None if session not found."""
    manager = _manager(context)
    meta = manager.get_session_metadata(session_name)
    if not meta:
        return None
    try:
        last_output = tmux_controller.capture_pane(session_name, lines=_default_log_lines(context))
    except Exception as e:
        last_output = str(e)
    lines = [
        f"Session: {meta['session_name']}",
        f"Provider: {meta['provider_id']}",
        f"Mode: {meta['mode']}",
        "",
        "Last output:",
        last_output or "(empty)",
    ]
    return "\n".join(lines)


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Session status: /status or /status <session>. Shows name, provider, mode, last output."""
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
        await update.message.reply_text("No current session. Use /status <session> or /use <name>.")
        return
    status_text = get_status_text(context, session_name)
    if status_text is None:
        await update.message.reply_text(f"Session not found: {session_name}")
        return
    await update.message.reply_text(status_text)


async def handle_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Last N lines: /logs or /logs <session>."""
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
        await update.message.reply_text("No current session. Use /logs <session> or /use <name>.")
        return
    logs_text = get_logs_text(context, session_name)
    if logs_text is None:
        await update.message.reply_text(f"Session not found: {session_name}")
        return
    await update.message.reply_text(logs_text)


async def handle_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command history: /history or /history <session>."""
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
        await update.message.reply_text("No current session. Use /history <session> or /use <name>.")
        return
    if not _manager(context).get_session_metadata(session_name):
        await update.message.reply_text(f"Session not found: {session_name}")
        return
    entries = _history(context).get_last_for_session(session_name, limit=50, chat_id=chat_id)
    if not entries:
        await update.message.reply_text("No command history for this session.")
        return
    lines = [f"{ts}: {cmd}" for cmd, ts in reversed(entries)]
    await update.message.reply_text("\n".join(lines))
