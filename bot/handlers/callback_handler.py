from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.keyboards.main_keyboard import MainKeyboard

router = Router()


@router.callback_query(F.data.startswith("download_video_"))
async def download_video_callback(callback: CallbackQuery, state: FSMContext):
    """Обробка callback для завантаження відео"""
    try:
        video_id = callback.data.split("_")[-1]
        logger.info(f"Користувач {callback.from_user.id} хоче завантажити відео {video_id}")
        
        # Отримуємо дані зі стану
        state_data = await state.get_data()
        video_info = state_data.get('video_info')
        
        if not video_info:
            await callback.answer("❌ Інформація про відео втрачена. Спробуйте ще раз.", show_alert=True)
            return
        
        await callback.message.edit_text(
            "🚧 **Функція завантаження відео**\n\n"
            "Завантаження відео буде реалізовано в наступних версіях.\n"
            "Наразі доступна тільки демонстрація інтерфейсу.\n\n"
            f"📹 **Відео:** {video_info.get('title', 'Невідомо')}\n"
            f"🎯 **Якість:** 720p (за замовчуванням)\n"
            f"📦 **Формат:** MP4",
            parse_mode="Markdown",
            reply_markup=MainKeyboard.get_back_to_menu()
        )
        
        await callback.answer("✅ Запит на завантаження відео прийнято")
        
    except Exception as e:
        logger.error(f"Помилка в download_video_callback: {e}")
        await callback.answer("❌ Виникла помилка", show_alert=True)


@router.callback_query(F.data.startswith("download_audio_"))
async def download_audio_callback(callback: CallbackQuery, state: FSMContext):
    """Обробка callback для завантаження аудіо"""
    try:
        video_id = callback.data.split("_")[-1]
        logger.info(f"Користувач {callback.from_user.id} хоче завантажити аудіо {video_id}")
        
        # Отримуємо дані зі стану
        state_data = await state.get_data()
        video_info = state_data.get('video_info')
        
        if not video_info:
            await callback.answer("❌ Інформація про відео втрачена. Спробуйте ще раз.", show_alert=True)
            return
        
        await callback.message.edit_text(
            "🚧 **Функція завантаження аудіо**\n\n"
            "Завантаження аудіо буде реалізовано в наступних версіях.\n"
            "Наразі доступна тільки демонстрація інтерфейсу.\n\n"
            f"🎵 **Трек:** {video_info.get('title', 'Невідомо')}\n"
            f"🎯 **Якість:** 128 kbps (за замовчуванням)\n"
            f"📦 **Формат:** MP3",
            parse_mode="Markdown",
            reply_markup=MainKeyboard.get_back_to_menu()
        )
        
        await callback.answer("✅ Запит на завантаження аудіо прийнято")
        
    except Exception as e:
        logger.error(f"Помилка в download_audio_callback: {e}")
        await callback.answer("❌ Виникла помилка", show_alert=True)


@router.callback_query(F.data.startswith("quality_settings_"))
async def quality_settings_callback(callback: CallbackQuery):
    """Обробка callback для налаштувань якості"""
    try:
        video_id = callback.data.split("_")[-1]
        
        await callback.message.edit_text(
            "⚙️ **Налаштування якості**\n\n"
            "Функція вибору якості буде реалізована в наступних версіях.\n\n"
            "Доступні якості відео:\n"
            "• 360p - Стандартна якість\n"
            "• 480p - Покращена якість\n"
            "• 720p - HD якість\n"
            "• 1080p - Full HD якість\n\n"
            "Доступні якості аудіо:\n"
            "• 128 kbps - Стандартна якість\n"
            "• 192 kbps - Хороша якість\n"
            "• 256 kbps - Висока якість\n"
            "• 320 kbps - Максимальна якість",
            parse_mode="Markdown",
            reply_markup=MainKeyboard.get_back_to_menu()
        )
        
        await callback.answer("⚙️ Налаштування якості")
        
    except Exception as e:
        logger.error(f"Помилка в quality_settings_callback: {e}")
        await callback.answer("❌ Виникла помилка", show_alert=True)


@router.callback_query(F.data == "cancel_download")
async def cancel_download_callback(callback: CallbackQuery, state: FSMContext):
    """Обробка callback для скасування завантаження"""
    try:
        await state.clear()
        
        await callback.message.edit_text(
            "❌ **Завантаження скасовано**\n\n"
            "Ви можете почати нове завантаження, надіславши посилання на YouTube відео "
            "або використавши кнопки меню.",
            parse_mode="Markdown",
            reply_markup=MainKeyboard.get_back_to_menu()
        )
        
        await callback.answer("❌ Завантаження скасовано")
        
    except Exception as e:
        logger.error(f"Помилка в cancel_download_callback: {e}")
        await callback.answer("❌ Виникла помилка", show_alert=True)


@router.callback_query(F.data.startswith("back_to_video_"))
async def back_to_video_callback(callback: CallbackQuery, state: FSMContext):
    """Повернення до інформації про відео"""
    try:
        # Отримуємо дані зі стану
        state_data = await state.get_data()
        video_info = state_data.get('video_info')
        
        if not video_info:
            await callback.answer("❌ Інформація про відео втрачена", show_alert=True)
            return
        
        # Відновлюємо повідомлення з інформацією про відео
        info_text = (
            f"🎬 **{video_info.get('title', 'Невідомо')}**\n\n"
            f"👤 **Канал:** {video_info.get('uploader', 'Невідомо')}\n"
            f"⏱ **Тривалість:** {video_info.get('duration_formatted', 'Невідомо')}\n"
        )
        
        if video_info.get('view_count'):
            info_text += f"👁 **Перегляди:** {video_info['view_count']:,}\n"
        
        if video_info.get('filesize_mb'):
            info_text += f"📦 **Приблизний розмір:** {video_info['filesize_mb']} МБ\n"
        
        info_text += (
            f"\n📥 **Виберіть тип завантаження:**\n"
            f"• Відео - завантажити з відео та звуком\n"
            f"• Аудіо - тільки звукова доріжка в MP3"
        )
        
        from downloader.models.video_info import VideoInfo
        from bot.keyboards.download_keyboard import DownloadKeyboard
        
        # Створюємо об'єкт VideoInfo для клавіатури
        video_obj = VideoInfo(
            id=video_info.get('id', ''),
            title=video_info.get('title', ''),
            url=video_info.get('url', '')
        )
        
        await callback.message.edit_text(
            info_text,
            parse_mode="Markdown",
            reply_markup=DownloadKeyboard.get_video_info_keyboard(video_obj)
        )
        
        await callback.answer("🔙 Повернення до відео")
        
    except Exception as e:
        logger.error(f"Помилка в back_to_video_callback: {e}")
        await callback.answer("❌ Виникла помилка", show_alert=True)


@router.callback_query()
async def unknown_callback(callback: CallbackQuery):
    """Обробка невідомих callback запитів"""
    logger.warning(f"Невідомий callback: {callback.data} від користувача {callback.from_user.id}")
    await callback.answer("❓ Невідома команда", show_alert=True)