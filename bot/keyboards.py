from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def download_options_keyboard(url: str) -> InlineKeyboardMarkup:
    """Return inline keyboard with audio/video download buttons."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎵 Завантажити аудіо", callback_data=f"audio|{url}"),
                InlineKeyboardButton("🎥 Завантажити відео", callback_data=f"video|{url}"),
            ]
        ]
    )