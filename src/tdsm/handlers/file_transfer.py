"""File transfer handlers: /download, /upload; handle document messages for upload."""

from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

from tdsm import tmux_controller
from tdsm.file_transfer import (
    FileTransferError,
    resolve_and_validate_path,
    download_file,
    zip_folder,
    save_uploaded_files,
    extract_zip_safe,
)


def _config(context: ContextTypes.DEFAULT_TYPE):
    return context.bot_data["config"]


def _session_context(context: ContextTypes.DEFAULT_TYPE):
    return context.bot_data["session_context"]


def _get_cwd_and_base(session_name: str, context: ContextTypes.DEFAULT_TYPE):
    config = _config(context)
    cwd = tmux_controller.get_session_cwd(session_name)
    if not cwd:
        raise FileTransferError("Could not get session working directory.")
    base = config.file_transfer_base_path.strip() or None
    return cwd, base


async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /download <path> or /dl <path>: send file or folder as ZIP."""
    if not update.message or not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    ctx = _session_context(context)
    current = ctx.get_current_session(chat_id)
    if not current:
        await update.message.reply_text(
            "No current session. Use /use <name> or /new <name> [provider]."
        )
        return

    text = (update.message.text or "").strip()
    parts = text.split(maxsplit=1)
    path_arg = (parts[1] if len(parts) > 1 else "").strip()
    if not path_arg:
        await update.message.reply_text("Usage: /download <path> or /dl <path>")
        return

    config = _config(context)
    try:
        cwd, base = _get_cwd_and_base(current, context)
        path = resolve_and_validate_path(
            user_path=path_arg,
            cwd=cwd,
            allowed_base_path=base,
            exists_required=True,
        )
        if path.is_file():
            download_file(path, config.file_download_max_size)
            with open(path, "rb") as f:
                await update.message.reply_document(document=f, filename=path.name)
        elif path.is_dir():
            zip_buf, filename = zip_folder(path, config.zip_max_size)
            await update.message.reply_document(document=zip_buf, filename=filename)
        else:
            await update.message.reply_text("Path is not a file or directory.")
    except FileTransferError as e:
        await update.message.reply_text(f"Download error: {e.message}")


async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /upload [path] or /upload --extract [path]: set destination and wait for document(s)."""
    if not update.message or not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    ctx = _session_context(context)
    current = ctx.get_current_session(chat_id)
    if not current:
        await update.message.reply_text(
            "No current session. Use /use <name> or /new <name> [provider]."
        )
        return

    text = (update.message.text or "").strip()
    parts = text.split()
    extract = False
    path_arg = ""
    i = 1
    if i < len(parts) and parts[i] == "--extract":
        extract = True
        i += 1
    if i < len(parts):
        path_arg = " ".join(parts[i:]).strip()

    config = _config(context)
    try:
        cwd, base = _get_cwd_and_base(current, context)
        dest = resolve_and_validate_path(
            user_path=path_arg or ".",
            cwd=cwd,
            allowed_base_path=base,
            exists_required=False,
        )
        # Upload path is always the destination directory
        dest_dir = dest
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)
        context.chat_data["file_upload_dest"] = str(dest_dir)
        context.chat_data["file_upload_extract"] = extract
        context.chat_data["file_upload_session"] = current
        await update.message.reply_text(
            "Send the file(s) now. For a single ZIP with --extract, I will extract it to the destination."
        )
    except FileTransferError as e:
        await update.message.reply_text(f"Upload error: {e.message}")


async def handle_document_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle a message that contains a document (upload)."""
    if not update.message or not update.effective_chat or not update.message.document:
        return
    chat_id = update.effective_chat.id
    dest_dir = context.chat_data.get("file_upload_dest")
    extract = context.chat_data.get("file_upload_extract", False)
    session_name = context.chat_data.get("file_upload_session")

    # Optional: caption can override destination, e.g. "/upload ./path"
    caption = (update.message.caption or "").strip()
    if caption.lower().startswith("/upload"):
        parts = caption.split(maxsplit=1)
        path_arg = (parts[1] if len(parts) > 1 else "").strip()
        ctx = _session_context(context)
        current = ctx.get_current_session(chat_id)
        if current and path_arg:
            try:
                cwd, base = _get_cwd_and_base(current, context)
                dest = resolve_and_validate_path(
                    user_path=path_arg,
                    cwd=cwd,
                    allowed_base_path=base,
                    exists_required=False,
                )
                dest_dir = str(dest)
                session_name = current
            except FileTransferError:
                pass

    if not dest_dir or not session_name:
        await update.message.reply_text(
            "Use /upload [path] first (or /upload --extract [path] for ZIP), then send the file(s)."
        )
        return

    config = _config(context)
    doc = update.message.document
    file = await context.bot.get_file(doc.file_id)
    data = await file.download_as_bytearray()
    bytes_data = bytes(data)

    try:
        dest_path = Path(dest_dir)
        is_zip = doc.file_name and doc.file_name.lower().endswith(".zip")
        if extract and is_zip:
            extract_zip_safe(bytes_data, dest_path, config.zip_max_size)
            await update.message.reply_text("ZIP extracted successfully.")
        else:
            save_uploaded_files(
                dest_path,
                [(doc.file_name or "uploaded_file", bytes_data)],
                config.file_upload_max_size,
            )
            await update.message.reply_text("File saved.")
    except FileTransferError as e:
        await update.message.reply_text(f"Upload error: {e.message}")
    finally:
        context.chat_data.pop("file_upload_dest", None)
        context.chat_data.pop("file_upload_extract", None)
        context.chat_data.pop("file_upload_session", None)
