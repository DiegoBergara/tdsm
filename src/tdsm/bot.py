"""Bot entry point: load config, init DB and schema, init registry and providers, register router, start polling."""

import logging

from telegram.ext import Application, MessageHandler, filters

from tdsm.config import load as load_config
from tdsm.db import init_db
from tdsm.session_context import SessionContextStore
from tdsm.history_store import HistoryStore
from tdsm.session_manager import SessionManager
from tdsm.providers import ProviderRegistry, register_builtin_providers
from tdsm.command_router import dispatch

logger = logging.getLogger(__name__)


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
        .build()
    )
    application.bot_data["config"] = config
    application.bot_data["session_context"] = session_context
    application.bot_data["session_manager"] = session_manager
    application.bot_data["history_store"] = history_store
    application.bot_data["provider_registry"] = registry

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dispatch))
    application.add_handler(MessageHandler(filters.COMMAND, dispatch))

    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=["message"])
