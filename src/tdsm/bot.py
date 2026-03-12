"""Bot entry point: load config, init DB and schema, init registry and providers, register router, start polling."""

import logging

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from tdsm.config import load as load_config
from tdsm.db import init_db
from tdsm.session_context import SessionContextStore
from tdsm.history_store import HistoryStore
from tdsm.session_manager import SessionManager
from tdsm.providers import ProviderRegistry, register_builtin_providers
from tdsm.command_router import dispatch

logger = logging.getLogger(__name__)


async def _post_init(application: Application) -> None:
    """Remove webhook so polling receives updates (e.g. after switching from webhook deployment)."""
    await application.bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook removed; polling will receive updates.")


async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log handler errors so /start and other commands don't fail silently."""
    logger.exception("Error while handling update: %s", context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Error interno. Revisa los logs del bot (LOG_LEVEL=DEBUG)."
        )


def main() -> None:
    config = load_config()
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, config.log_level.upper(), logging.INFO),
    )
    init_db(config.database_path)
    session_context = SessionContextStore(config.database_path, use_cache=True)
    history_store = HistoryStore(config.database_path)
    registry = ProviderRegistry()
    register_builtin_providers(registry)
    session_manager = SessionManager(config.database_path, session_context)

    application = (
        Application.builder()
        .token(config.telegram_bot_token)
        .post_init(_post_init)
        .build()
    )
    application.bot_data["config"] = config
    application.bot_data["session_context"] = session_context
    application.bot_data["session_manager"] = session_manager
    application.bot_data["history_store"] = history_store
    application.bot_data["provider_registry"] = registry

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dispatch))
    application.add_handler(MessageHandler(filters.COMMAND, dispatch))
    application.add_handler(MessageHandler(filters.Document.ALL, dispatch))
    application.add_error_handler(_error_handler)

    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=["message"])
