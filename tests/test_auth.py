"""Tests for command parsing and routing (auth allowlist, handler dispatch)."""

import pytest

from tdsm.auth import is_allowed, check_access, AccessDenied


def test_is_allowed():
    assert is_allowed(1, [1, 2, 3]) is True
    assert is_allowed(4, [1, 2, 3]) is False


def test_check_access_allowed():
    check_access(1, [1, 2, 3])


def test_check_access_denied():
    with pytest.raises(AccessDenied) as exc_info:
        check_access(99, [1, 2, 3])
    assert "not in the allowlist" in exc_info.value.message or "Access denied" in exc_info.value.message
