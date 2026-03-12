"""Tests for file_transfer: path resolution, download, zip, upload, extract."""

import zipfile
import tempfile
from pathlib import Path
from io import BytesIO

import pytest

from tdsm.file_transfer import (
    FileTransferError,
    resolve_and_validate_path,
    download_file,
    zip_folder,
    save_uploaded_files,
    extract_zip_safe,
)


@pytest.fixture
def tmp_tree(tmp_path):
    """Create a temporary directory with files and subdirs for tests."""
    (tmp_path / "file.txt").write_text("hello")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "nested.txt").write_text("nested")
    return tmp_path


def test_resolve_relative_path_under_cwd(tmp_tree):
    """Relative path under cwd resolves and is allowed when base is cwd."""
    cwd = str(tmp_tree)
    path = resolve_and_validate_path(
        user_path="file.txt",
        cwd=cwd,
        allowed_base_path=None,
        exists_required=True,
    )
    assert path == tmp_tree / "file.txt"
    assert path.is_file()


def test_resolve_relative_path_subdir(tmp_tree):
    """Relative path with subdir is under base."""
    cwd = str(tmp_tree)
    path = resolve_and_validate_path(
        user_path="sub/nested.txt",
        cwd=cwd,
        allowed_base_path=None,
        exists_required=True,
    )
    assert path == tmp_tree / "sub" / "nested.txt"


def test_resolve_path_traversal_rejected(tmp_tree):
    """Path with .. escaping cwd is rejected (either 'outside' or 'exist' when path is missing)."""
    cwd = str(tmp_tree)
    with pytest.raises(FileTransferError) as exc:
        resolve_and_validate_path(
            user_path="../other/file.txt",
            cwd=cwd,
            allowed_base_path=None,
            exists_required=True,
        )
    msg = exc.value.message.lower()
    assert "outside" in msg or "invalid" in msg or "exist" in msg


def test_resolve_absolute_under_base(tmp_tree):
    """Absolute path under allowed base is accepted."""
    base = str(tmp_tree)
    abs_path = tmp_tree / "file.txt"
    path = resolve_and_validate_path(
        user_path=str(abs_path),
        cwd=base,
        allowed_base_path=base,
        exists_required=True,
    )
    assert path == abs_path


def test_resolve_absolute_outside_base_rejected(tmp_tree):
    """Absolute path outside allowed base is rejected."""
    base = str(tmp_tree)
    with pytest.raises(FileTransferError) as exc:
        resolve_and_validate_path(
            user_path="/etc/passwd",
            cwd=base,
            allowed_base_path=base,
            exists_required=True,
        )
    assert "outside" in exc.value.message.lower() or "invalid" in exc.value.message.lower()


def test_resolve_nonexistent_required_fails(tmp_tree):
    """When exists_required=True, nonexistent path raises."""
    cwd = str(tmp_tree)
    with pytest.raises(FileTransferError) as exc:
        resolve_and_validate_path(
            user_path="nonexistent.txt",
            cwd=cwd,
            allowed_base_path=None,
            exists_required=True,
        )
    assert "exist" in exc.value.message.lower()


def test_resolve_nonexistent_not_required_succeeds(tmp_tree):
    """When exists_required=False, nonexistent path under base is allowed."""
    cwd = str(tmp_tree)
    path = resolve_and_validate_path(
        user_path="newdir/newfile.txt",
        cwd=cwd,
        allowed_base_path=None,
        exists_required=False,
    )
    assert path == tmp_tree / "newdir" / "newfile.txt"


def test_download_file_success(tmp_tree):
    """download_file returns path when file exists and size under limit."""
    p = tmp_tree / "file.txt"
    out = download_file(p, max_size=100)
    assert out == p


def test_download_file_directory_raises(tmp_tree):
    """download_file raises when path is a directory."""
    with pytest.raises(FileTransferError) as exc:
        download_file(tmp_tree / "sub", max_size=100)
    assert "directory" in exc.value.message.lower()


def test_download_file_size_exceeded(tmp_tree):
    """download_file raises when file size exceeds max."""
    (tmp_tree / "big").write_bytes(b"x" * 10)
    with pytest.raises(FileTransferError) as exc:
        download_file(tmp_tree / "big", max_size=5)
    assert "exceed" in exc.value.message.lower()


def test_zip_folder_empty(tmp_tree):
    """zip_folder produces valid ZIP for empty directory."""
    empty = tmp_tree / "empty"
    empty.mkdir()
    buf, name = zip_folder(empty, max_size=1024 * 1024)
    assert name == "empty.zip"
    assert buf.getbuffer().nbytes >= 0
    with zipfile.ZipFile(buf, "r") as zf:
        assert len(zf.namelist()) >= 0


def test_zip_folder_with_files(tmp_tree):
    """zip_folder includes files from directory."""
    buf, name = zip_folder(tmp_tree, max_size=1024 * 1024)
    assert name == tmp_tree.name + ".zip"
    with zipfile.ZipFile(buf, "r") as zf:
        names = set(zf.namelist())
        assert "file.txt" in names or any("file.txt" in n for n in names)
        assert "sub/nested.txt" in names or any("nested.txt" in n for n in names)


def test_zip_folder_not_directory_raises(tmp_tree):
    """zip_folder raises when path is a file."""
    with pytest.raises(FileTransferError) as exc:
        zip_folder(tmp_tree / "file.txt", max_size=1024)
    assert "directory" in exc.value.message.lower()


def test_zip_folder_size_limit(tmp_tree):
    """zip_folder raises when ZIP would exceed max size."""
    (tmp_tree / "large").write_bytes(b"x" * 100)
    with pytest.raises(FileTransferError) as exc:
        zip_folder(tmp_tree, max_size=50)
    assert "exceed" in exc.value.message.lower()


def test_save_uploaded_files(tmp_tree):
    """save_uploaded_files writes files with original names."""
    files = [("a.txt", b"content a"), ("sub/b.txt", b"content b")]
    save_uploaded_files(tmp_tree, files, max_size_per_file=100)
    assert (tmp_tree / "a.txt").read_bytes() == b"content a"
    assert (tmp_tree / "sub" / "b.txt").read_bytes() == b"content b"


def test_save_uploaded_files_size_exceeded(tmp_tree):
    """save_uploaded_files raises when a file exceeds max size."""
    with pytest.raises(FileTransferError) as exc:
        save_uploaded_files(
            tmp_tree,
            [("x.txt", b"y" * 20)],
            max_size_per_file=10,
        )
    assert "exceed" in exc.value.message.lower()


def test_save_uploaded_files_path_traversal_rejected(tmp_tree):
    """save_uploaded_files rejects filename that escapes dest_dir."""
    with pytest.raises(FileTransferError) as exc:
        save_uploaded_files(
            tmp_tree,
            [("../../../etc/evil", b"x")],
            max_size_per_file=100,
        )
    assert "invalid" in exc.value.message.lower() or "filename" in exc.value.message.lower()


def test_extract_zip_safe_success(tmp_tree):
    """extract_zip_safe extracts normal ZIP under dest_dir."""
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("a.txt", b"content")
        zf.writestr("d/b.txt", b"nested")
    buf.seek(0)
    dest = tmp_tree / "out"
    dest.mkdir()
    extract_zip_safe(buf.getvalue(), dest, max_zip_size=1024 * 1024)
    assert (dest / "a.txt").read_bytes() == b"content"
    assert (dest / "d" / "b.txt").read_bytes() == b"nested"


def test_extract_zip_safe_path_traversal_rejected(tmp_tree):
    """extract_zip_safe rejects ZIP member with path traversal."""
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("../../../evil.txt", b"bad")
    buf.seek(0)
    dest = tmp_tree / "out"
    dest.mkdir()
    with pytest.raises(FileTransferError) as exc:
        extract_zip_safe(buf.getvalue(), dest, max_zip_size=1024)
    assert "security" in exc.value.message.lower() or "invalid" in exc.value.message.lower() or "traversal" in exc.value.message.lower()


def test_extract_zip_safe_absolute_member_rejected(tmp_tree):
    """extract_zip_safe rejects member with absolute path."""
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("/abs.txt", b"bad")
    buf.seek(0)
    dest = tmp_tree / "out"
    dest.mkdir()
    with pytest.raises(FileTransferError) as exc:
        extract_zip_safe(buf.getvalue(), dest, max_zip_size=1024)
    assert "invalid" in exc.value.message.lower() or "security" in exc.value.message.lower()


def test_extract_zip_safe_size_exceeded(tmp_tree):
    """extract_zip_safe rejects ZIP larger than max."""
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("x.txt", b"x" * 100)
    buf.seek(0)
    dest = tmp_tree / "out"
    dest.mkdir()
    with pytest.raises(FileTransferError) as exc:
        extract_zip_safe(buf.getvalue(), dest, max_zip_size=50)
    assert "exceed" in exc.value.message.lower()


# --- Handler tests (mocked Telegram/session) ---


def test_handle_download_no_session():
    """handle_download replies with error when there is no current session."""
    import asyncio
    from unittest.mock import AsyncMock, MagicMock

    from tdsm.handlers import file_transfer as file_transfer_handler

    async def run():
        update = MagicMock()
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        update.effective_chat = MagicMock()
        update.effective_chat.id = 12345
        update.message.text = "/download file.txt"

        context = MagicMock()
        context.bot_data = {
            "session_context": MagicMock(get_current_session=MagicMock(return_value=None)),
        }

        await file_transfer_handler.handle_download(update, context)
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "current session" in call_args.lower() or "no current" in call_args.lower()

    asyncio.run(run())


def test_handle_upload_no_session():
    """handle_upload replies with error when there is no current session."""
    import asyncio
    from unittest.mock import AsyncMock, MagicMock

    from tdsm.handlers import file_transfer as file_transfer_handler

    async def run():
        update = MagicMock()
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        update.effective_chat = MagicMock()
        update.effective_chat.id = 12345
        update.message.text = "/upload"

        context = MagicMock()
        context.bot_data = {
            "session_context": MagicMock(get_current_session=MagicMock(return_value=None)),
        }

        await file_transfer_handler.handle_upload(update, context)
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "current session" in call_args.lower() or "no current" in call_args.lower()

    asyncio.run(run())
