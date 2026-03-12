"""Shared helpers for update/context in command handlers."""

from telegram import Update
from telegram.ext import ContextTypes


def get_command_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Return the message text to use when handling a command.
    When the command router has normalized the text (e.g. /new_ -> /new), it is stored
    in context.user_data and takes precedence. Otherwise use update.message.text.
    """
    if context and context.user_data and "_command_text" in context.user_data:
        return context.user_data.pop("_command_text", "")
    if update and update.message and update.message.text:
        return update.message.text.strip()
    return ""
