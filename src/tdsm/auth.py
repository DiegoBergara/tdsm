"""Authorization: allowlist check before routing. Rejects non-allowlisted users with clear response."""

from typing import List

ACCESS_DENIED_MESSAGE = "Access denied. Your user ID is not in the allowlist."


def is_allowed(user_id: int, allowed_user_ids: List[int]) -> bool:
    """Return True if user_id is in the allowlist."""
    return user_id in allowed_user_ids


def check_access(user_id: int, allowed_user_ids: List[int]) -> None:
    """
    Raise AccessDenied if user_id is not in the allowlist.
    Call this before processing any command or message.
    """
    if not is_allowed(user_id, allowed_user_ids):
        raise AccessDenied(ACCESS_DENIED_MESSAGE)


class AccessDenied(Exception):
    """Raised when a user is not in the allowlist."""

    def __init__(self, message: str = ACCESS_DENIED_MESSAGE):
        self.message = message
        super().__init__(message)
