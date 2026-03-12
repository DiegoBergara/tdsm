"""Configuration from environment variables. Fails fast on missing required vars."""

import os
from typing import List


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value or not value.strip():
        raise SystemExit(f"Missing required env: {name}")
    return value.strip()


def _optional(name: str, default: str) -> str:
    return (os.environ.get(name) or default).strip()


def _optional_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        raise SystemExit(f"Invalid {name}: expected integer, got {raw!r}")


def _allowed_user_ids() -> List[int]:
    raw = _require("ALLOWED_USER_IDS")
    ids: List[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except ValueError:
            raise SystemExit(f"Invalid ALLOWED_USER_IDS: expected comma-separated integers, got {raw!r}")
    if not ids:
        raise SystemExit("ALLOWED_USER_IDS must contain at least one user id")
    return ids


def load() -> "Config":
    """Load config from environment. Exits if required vars are missing."""
    return Config(
        telegram_bot_token=_require("TELEGRAM_BOT_TOKEN"),
        allowed_user_ids=_allowed_user_ids(),
        database_path=_optional("DATABASE_PATH", "./data/tdsm.db"),
        log_level=_optional("LOG_LEVEL", "INFO"),
        default_log_lines=_parse_default_log_lines(),
        file_transfer_base_path=_optional("FILE_TRANSFER_BASE_PATH", ""),
        file_download_max_size=_optional_int("FILE_DOWNLOAD_MAX_SIZE", 20 * 1024 * 1024),  # 20 MiB
        file_upload_max_size=_optional_int("FILE_UPLOAD_MAX_SIZE", 20 * 1024 * 1024),  # 20 MiB
        zip_max_size=_optional_int("ZIP_MAX_SIZE", 20 * 1024 * 1024),  # 20 MiB
    )


def _parse_default_log_lines() -> int:
    raw = _optional("DEFAULT_LOG_LINES", "50")
    try:
        n = int(raw)
    except ValueError:
        raise SystemExit(f"Invalid DEFAULT_LOG_LINES: expected integer, got {raw!r}")
    if n < 1:
        raise SystemExit("DEFAULT_LOG_LINES must be >= 1")
    return n


class Config:
    """Runtime configuration."""

    __slots__ = (
        "telegram_bot_token",
        "allowed_user_ids",
        "database_path",
        "log_level",
        "default_log_lines",
        "file_transfer_base_path",
        "file_download_max_size",
        "file_upload_max_size",
        "zip_max_size",
    )

    def __init__(
        self,
        *,
        telegram_bot_token: str,
        allowed_user_ids: List[int],
        database_path: str = "./data/tdsm.db",
        log_level: str = "INFO",
        default_log_lines: int = 50,
        file_transfer_base_path: str = "",
        file_download_max_size: int = 20 * 1024 * 1024,
        file_upload_max_size: int = 20 * 1024 * 1024,
        zip_max_size: int = 20 * 1024 * 1024,
    ):
        self.telegram_bot_token = telegram_bot_token
        self.allowed_user_ids = allowed_user_ids
        self.database_path = database_path
        self.log_level = log_level
        self.default_log_lines = default_log_lines
        self.file_transfer_base_path = file_transfer_base_path
        self.file_download_max_size = file_download_max_size
        self.file_upload_max_size = file_upload_max_size
        self.zip_max_size = zip_max_size
