"""Pytest fixtures: temp DB, mock tmux."""

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

from tdsm.db import SCHEMA


@pytest.fixture
def db_path():
    """Temporary SQLite database path with schema."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass
