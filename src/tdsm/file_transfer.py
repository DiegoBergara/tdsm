"""
File transfer: safe path resolution, file download, folder ZIP, file upload, ZIP extract.
All paths are validated to stay under an allowed base path (or session cwd if not configured).
"""

import os
import zipfile
import tempfile
from pathlib import Path
from typing import List, Tuple
from io import BytesIO


class FileTransferError(Exception):
    """Raised when a file transfer operation is rejected (security, size, not found)."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def resolve_and_validate_path(
    *,
    user_path: str,
    cwd: str,
    allowed_base_path: str | None,
    exists_required: bool = True,
) -> Path:
    """
    Resolve user_path (relative to cwd or absolute) to an absolute path and validate
    it is under the allowed base. If exists_required=True, path must exist.
    Raises FileTransferError if invalid.
    """
    if not user_path or not user_path.strip():
        raise FileTransferError("Path cannot be empty.")

    base = Path(cwd).resolve()
    if allowed_base_path and allowed_base_path.strip():
        base = Path(allowed_base_path.strip()).resolve()
        if not base.is_dir():
            raise FileTransferError("Configured base path is not a directory.")
    # Resolve user path: if absolute, use as-is (then check under base); else relative to cwd
    p = Path(user_path.strip())
    if not p.is_absolute():
        p = (Path(cwd) / p).resolve()
    else:
        p = p.resolve()

    try:
        p = p.resolve(strict=False)
        if exists_required and not p.exists():
            raise FileTransferError(f"Path does not exist: {p}")
        # Ensure resolved path is under base (use realpath when path exists)
        real_base = base.resolve()
        real_p = p.resolve()
        if p.exists():
            try:
                real_base = real_base.resolve(strict=True)
                real_p = real_p.resolve(strict=True)
            except OSError:
                pass
        if not str(real_p).startswith(str(real_base) + os.sep) and real_p != real_base:
            raise FileTransferError("Path is outside the allowed directory.")
    except FileTransferError:
        raise
    except Exception as e:
        raise FileTransferError(f"Invalid path: {e}") from e

    return p


def download_file(path: Path, max_size: int) -> Path:
    """
    Validate path is a file and size <= max_size; return path to the file.
    Raises FileTransferError if directory, not found, or size exceeded.
    """
    if not path.is_file():
        if path.is_dir():
            raise FileTransferError("Path is a directory; use folder download for directories.")
        raise FileTransferError("Path is not a file or does not exist.")
    size = path.stat().st_size
    if size == 0:
        raise FileTransferError("File is empty; Telegram does not allow sending empty files.")
    if size > max_size:
        raise FileTransferError(f"File size ({size}) exceeds maximum allowed ({max_size}).")
    return path


def zip_folder(path: Path, max_size: int) -> Tuple[BytesIO, str]:
    """
    Create a ZIP of the directory at path. Returns (BytesIO with ZIP data, suggested filename).
    Raises FileTransferError if path is not a directory or ZIP would exceed max_size.
    """
    if not path.is_dir():
        raise FileTransferError("Path is not a directory.")
    buf = BytesIO()
    total = 0

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(path):
            for name in files:
                full = Path(root) / name
                try:
                    arcname = os.path.relpath(full, path)
                except ValueError:
                    arcname = full.name
                info = zipfile.ZipInfo.from_file(full, arcname=arcname)
                with open(full, "rb") as f:
                    data = f.read()
                total += len(data)
                if total > max_size:
                    raise FileTransferError(
                        f"ZIP size would exceed maximum allowed ({max_size})."
                    )
                zf.writestr(info, data)

    buf.seek(0)
    size = buf.getbuffer().nbytes
    if size > max_size:
        raise FileTransferError(f"ZIP size ({size}) exceeds maximum allowed ({max_size}).")
    return buf, path.name + ".zip"


def save_uploaded_files(
    dest_dir: Path,
    files: List[Tuple[str, bytes]],
    max_size_per_file: int,
) -> None:
    """
    Write each (filename, content) into dest_dir with original filename.
    Validates each file size and that dest paths stay under dest_dir.
    Raises FileTransferError on violation.
    """
    dest_dir = dest_dir.resolve()
    if dest_dir.exists() and dest_dir.is_file():
        raise FileTransferError(
            "Destination path is a file; use a directory path for uploads (e.g. . or folder name)."
        )
    for filename, content in files:
        if len(content) > max_size_per_file:
            raise FileTransferError(
                f"File {filename} size ({len(content)}) exceeds maximum ({max_size_per_file})."
            )
        # Prevent path traversal in filename
        safe = (dest_dir / filename).resolve()
        if not str(safe).startswith(str(dest_dir) + os.sep) and safe != dest_dir:
            raise FileTransferError(f"Invalid filename: {filename}")
        if safe.parent.exists() and safe.parent.is_file():
            raise FileTransferError(
                f"Cannot save here: '{safe.parent}' exists as a file, not a directory."
            )
        safe.parent.mkdir(parents=True, exist_ok=True)
        safe.write_bytes(content)


def extract_zip_safe(
    zip_data: bytes,
    dest_dir: Path,
    max_zip_size: int,
) -> None:
    """
    Extract ZIP bytes into dest_dir. Validates total ZIP size and that every member
    resolves under dest_dir (no path traversal). Raises FileTransferError on violation.
    """
    if len(zip_data) > max_zip_size:
        raise FileTransferError(
            f"ZIP size ({len(zip_data)}) exceeds maximum allowed ({max_zip_size})."
        )
    dest_dir = dest_dir.resolve()
    with zipfile.ZipFile(BytesIO(zip_data), "r") as zf:
        for info in zf.infolist():
            # Skip directory-only entries; resolve member name safely
            name = info.filename
            if name.startswith("/") or ".." in name:
                raise FileTransferError("ZIP contains invalid member path (security).")
            target = (dest_dir / name).resolve()
            if not str(target).startswith(str(dest_dir) + os.sep) and target != dest_dir:
                raise FileTransferError("ZIP contains path traversal (security).")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(info))
