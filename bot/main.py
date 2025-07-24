import asyncio
import logging

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, MessageHandler, filters

from .config import TELEGRAM_TOKEN
from .handlers import handle_download_callback, handle_message

logging.basicConfig(level=logging.INFO)


def run_bot() -> None:
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    # Register handlers
    application.add_handler(CallbackQueryHandler(handle_download_callback))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    logging.info("Starting Telegram bot...")

    application.run_polling()


if __name__ == "__main__":
    run_bot()