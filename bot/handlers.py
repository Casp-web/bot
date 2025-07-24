import re
import tempfile
from typing import Final

import requests
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from .config import DOWNLOADER_SERVICE_URL
from .keyboards import download_options_keyboard

YOUTUBE_REGEX: Final = re.compile(
    r"(?:https?://)?(?:www\.)?(?:m\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=|embed/|v/|.+\?v=)?([\w-]{11})"
)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages and suggest download options for YouTube links."""
    if not update.message or not update.message.text:
        return

    urls = YOUTUBE_REGEX.findall(update.message.text)
    if not urls:
        return  # Ignore messages without YouTube links

    # For simplicity take the first
    video_id = urls[0]
    url = f"https://youtu.be/{video_id}"

    await update.message.reply_text(
        "Оберіть формат завантаження:", reply_markup=download_options_keyboard(url)
    )


async def handle_download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses for downloading audio/video."""
    query = update.callback_query
    if not query:
        return

    await query.answer()

    data = query.data or ""
    try:
        download_type, url = data.split("|", 1)
    except ValueError:
        await query.edit_message_text("Невідомий запит.")
        return

    await query.edit_message_text("⏳ Завантаження... будь ласка, зачекайте")
    await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.UPLOAD_DOCUMENT)

    endpoint = f"{DOWNLOADER_SERVICE_URL}/download/{download_type}"
    try:
        with requests.post(endpoint, json={"url": url}, stream=True, timeout=600) as resp:
            resp.raise_for_status()
            # The filename is set in 'Content-Disposition'
            filename = resp.headers.get("Content-Disposition", "download").split("filename=")[-1].strip("\"")
            if not filename:
                filename = f"yt_{download_type}.{'mp3' if download_type == 'audio' else 'mp4'}"

            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                temp_path = tmp_file.name

        # Send file
        if download_type == "audio":
            await query.message.reply_audio(audio=open(temp_path, "rb"), filename=filename)
        else:
            await query.message.reply_video(video=open(temp_path, "rb"), filename=filename,supports_streaming=True)

        await query.edit_message_text("✅ Завантаження завершено!")
    except requests.RequestException as exc:
        await query.edit_message_text(f"❌ Помилка завантаження: {exc}")