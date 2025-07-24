from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.keyboards.main_keyboard import MainKeyboard
from bot.keyboards.download_keyboard import DownloadKeyboard
from downloader.services.youtube_service import YouTubeService
from utils.validators import URLValidator
from database.repositories.user_repository import UserRepository

router = Router()


@router.message(F.text.regexp(r'(?:youtube\.com|youtu\.be|music\.youtube\.com)'))
async def handle_youtube_url(message: Message, state: FSMContext, db_user=None, user_repo: UserRepository = None):
    """Автоматична обробка YouTube URL"""
    try:
        url = message.text.strip()
        logger.info(f"Отримано YouTube URL від користувача {message.from_user.id}: {url}")
        
        # Валідація URL
        url_validator = URLValidator()
        if not url_validator.is_valid_youtube_url(url):
            await message.answer(
                "❌ Невірне посилання на YouTube.\n\n"
                "🎯 **Підтримувані формати:**\n"
                "• `https://www.youtube.com/watch?v=VIDEO_ID`\n"
                "• `https://youtu.be/VIDEO_ID`\n"
                "• `https://www.youtube.com/shorts/VIDEO_ID`\n"
                "• `https://music.youtube.com/watch?v=VIDEO_ID`\n"
                "• `https://m.youtube.com/watch?v=VIDEO_ID`\n"
                "• `https://www.youtube.com/embed/VIDEO_ID`\n\n"
                "💡 **Підказка:** Просто скопіюйте посилання з адресного рядка браузера або кнопки 'Поділитися' на YouTube.",
                parse_mode="Markdown",
                reply_markup=MainKeyboard.get_main_menu()
            )
            return
        
        # Нормалізуємо URL
        normalized_url = url_validator.normalize_youtube_url(url)
        if not normalized_url:
            await message.answer(
                "❌ Не вдалося обробити посилання.",
                reply_markup=MainKeyboard.get_main_menu()
            )
            return
        
        # Перевіряємо ліміти користувача
        if db_user and user_repo:
            downloads_today = await user_repo.get_user_downloads_today(db_user.telegram_id)
            from config.settings.base import settings
            
            if downloads_today >= settings.MAX_DOWNLOADS_PER_USER_HOUR:
                await message.answer(
                    f"⚠️ Ви досягли денного ліміту завантажень ({settings.MAX_DOWNLOADS_PER_USER_HOUR}).\n"
                    f"Спробуйте завтра або зверніться до адміністратора.",
                    reply_markup=MainKeyboard.get_main_menu()
                )
                return
        
        # Показуємо повідомлення про обробку
        processing_msg = await message.answer(
            "🔍 Отримую інформацію про відео...\n"
            "⏳ Це може зайняти кілька секунд."
        )
        
        # Отримуємо інформацію про відео
        youtube_service = YouTubeService()
        video_info = await youtube_service.get_video_info(normalized_url)
        
        if not video_info:
            await processing_msg.edit_text(
                "❌ Не вдалося отримати інформацію про відео.\n\n"
                "Можливі причини:\n"
                "• Відео недоступне або приватне\n"
                "• Проблеми з мережею\n"
                "• Відео заблоковане в вашому регіоні",
                reply_markup=MainKeyboard.get_back_to_menu()
            )
            return
        
        # Перевіряємо обмеження
        from config.settings.base import settings
        
        # Перевірка тривалості
        if video_info.duration and video_info.duration > settings.MAX_DURATION_MINUTES * 60:
            await processing_msg.edit_text(
                f"❌ Відео занадто довге.\n\n"
                f"📏 Тривалість відео: {video_info.duration_formatted}\n"
                f"⚠️ Максимальна дозволена тривалість: {settings.MAX_DURATION_MINUTES} хвилин",
                reply_markup=MainKeyboard.get_back_to_menu()
            )
            return
        
        # Перевірка розміру (приблизно)
        if video_info.filesize_mb and video_info.filesize_mb > settings.MAX_FILE_SIZE_MB:
            await processing_msg.edit_text(
                f"❌ Файл занадто великий.\n\n"
                f"📦 Приблизний розмір: {video_info.filesize_mb} МБ\n"
                f"⚠️ Максимальний дозволений розмір: {settings.MAX_FILE_SIZE_MB} МБ",
                reply_markup=MainKeyboard.get_back_to_menu()
            )
            return
        
        # Формуємо інформацію про відео
        info_text = (
            f"🎬 **{video_info.title}**\n\n"
            f"👤 **Канал:** {video_info.uploader or 'Невідомо'}\n"
            f"⏱ **Тривалість:** {video_info.duration_formatted}\n"
            f"👁 **Перегляди:** {video_info.view_count:,}" if video_info.view_count else ""
        )
        
        if video_info.filesize_mb:
            info_text += f"\n📦 **Приблизний розмір:** {video_info.filesize_mb} МБ"
        
        info_text += (
            f"\n\n📥 **Виберіть тип завантаження:**\n"
            f"• Відео - завантажити з відео та звуком\n"
            f"• Аудіо - тільки звукова доріжка в MP3"
        )
        
        # Зберігаємо інформацію про відео в стані
        await state.update_data(
            video_info=video_info.__dict__,
            original_url=url,
            normalized_url=normalized_url
        )
        
        # Показуємо інформацію та клавіатуру
        try:
            await processing_msg.edit_text(
                info_text,
                parse_mode="Markdown",
                reply_markup=DownloadKeyboard.get_video_info_keyboard(video_info)
            )
        except Exception as e:
            # Якщо не вдалося відредагувати повідомлення, відправляємо нове
            await processing_msg.delete()
            await message.answer(
                info_text,
                parse_mode="Markdown",
                reply_markup=DownloadKeyboard.get_video_info_keyboard(video_info)
            )
        
    except Exception as e:
        logger.error(f"Помилка обробки YouTube URL: {e}")
        await message.answer(
            "❌ Виникла помилка при обробці посилання.\n"
            "Спробуйте ще раз або зверніться до адміністратора.",
            reply_markup=MainKeyboard.get_main_menu()
        )


@router.message(F.text.regexp(r'https?://[^\s]+'))
async def handle_other_url(message: Message):
    """Обробка інших URL (не YouTube)"""
    await message.answer(
        "❌ **Підтримуються тільки посилання на YouTube!**\n\n"
        "🎯 **Правильні приклади:**\n"
        "• `https://www.youtube.com/watch?v=dQw4w9WgXcQ`\n"
        "• `https://youtu.be/dQw4w9WgXcQ`\n"
        "• `https://www.youtube.com/shorts/dQw4w9WgXcQ`\n\n"
        "🚫 **Не підтримуються:**\n"
        "• Instagram, TikTok, Facebook відео\n"
        "• Інші відеохостинги\n"
        "• Прямі посилання на файли\n\n"
        "💡 Надішліть посилання на YouTube відео або скористайтеся головним меню.",
        parse_mode="Markdown",
        reply_markup=MainKeyboard.get_main_menu()
    )