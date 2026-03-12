"""Providers handler: /providers - list from registry with availability."""

from telegram import Update
from telegram.ext import ContextTypes

from tdsm.providers.registry import ProviderRegistry


def _registry(context: ContextTypes.DEFAULT_TYPE) -> ProviderRegistry:
    return context.bot_data["provider_registry"]


async def handle_providers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List providers with availability: /providers."""
    if not update.message:
        return
    lines = ["Providers:"]
    for provider, available in _registry(context).list_all():
        status = "available" if available else "unavailable"
        lines.append(f"- {provider.id} ({provider.display_name}) - {status}")
    await update.message.reply_text("\n".join(lines))
