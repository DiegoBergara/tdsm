"""Modes handler: /mode (cycle), /mode <mode> (set), /modes (list). Persist mode in session metadata."""

from telegram import Update
from telegram.ext import ContextTypes

from tdsm.session_context import SessionContextStore
from tdsm.session_manager import SessionManager
from tdsm.providers.registry import ProviderRegistry


def _manager(context: ContextTypes.DEFAULT_TYPE) -> SessionManager:
    return context.bot_data["session_manager"]


def _context_store(context: ContextTypes.DEFAULT_TYPE) -> SessionContextStore:
    return context.bot_data["session_context"]


def _registry(context: ContextTypes.DEFAULT_TYPE) -> ProviderRegistry:
    return context.bot_data["provider_registry"]


async def handle_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cycle or set mode: /mode or /mode <mode>. Uses current session."""
    if not update.message or not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    current_session = _context_store(context).get_current_session(chat_id)
    if not current_session:
        await update.message.reply_text("No current session. Use /use <name>.")
        return
    manager = _manager(context)
    meta = manager.get_session_metadata(current_session)
    if not meta:
        await update.message.reply_text(f"Session not found: {current_session}")
        return
    provider = _registry(context).get(meta["provider_id"])
    if not provider:
        await update.message.reply_text(f"Provider not found: {meta['provider_id']}")
        return
    parts = (update.message.text or "").split()
    if len(parts) >= 2:
        new_mode = parts[1].strip()
        if new_mode not in provider.get_modes():
            await update.message.reply_text(
                f"Invalid mode: {new_mode}. Available: {', '.join(provider.get_modes())}"
            )
            return
        manager.set_session_mode(current_session, new_mode)
        await update.message.reply_text(f"Mode set to {new_mode}.")
    else:
        next_mode = provider.next_mode(meta["mode"])
        manager.set_session_mode(current_session, next_mode)
        await update.message.reply_text(f"Mode: {next_mode}.")


async def handle_modes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List modes: /modes. Uses current session's provider."""
    if not update.message or not update.effective_chat:
        return
    current_session = _context_store(context).get_current_session(update.effective_chat.id)
    if not current_session:
        await update.message.reply_text("No current session. Use /use <name>.")
        return
    meta = _manager(context).get_session_metadata(current_session)
    if not meta:
        await update.message.reply_text(f"Session not found: {current_session}")
        return
    provider = _registry(context).get(meta["provider_id"])
    if not provider:
        await update.message.reply_text(f"Provider not found: {meta['provider_id']}")
        return
    modes = provider.get_modes()
    await update.message.reply_text("Available modes:\n" + "\n".join(modes))
