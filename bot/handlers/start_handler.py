from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main_keyboard import MainKeyboard
from database.models.base import get_async_session
from database.repositories.user_repository import UserRepository
from utils.validators import UserInputValidator

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    """Обробка команди /start"""
    try:
        # Очищуємо стан
        await state.clear()
        
        # Отримуємо сесію бази даних
        async for session in get_async_session():
            user_repo = UserRepository(session)
            
            # Створюємо або оновлюємо користувача
            user = await user_repo.create_or_update_user(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code or "uk"
            )
            
            # Перевіряємо чи не заблокований користувач
            if user.is_banned:
                await message.answer(
                    f"❌ Ваш акаунт заблокований.\n"
                    f"Причина: {user.ban_reason or 'Не вказана'}\n\n"
                    f"Зверніться до адміністратора для розблокування."
                )
                return
            
            break
        
        # Вітальне повідомлення
        welcome_text = (
            f"👋 Привіт, {message.from_user.first_name}!\n\n"
            f"🎬 Я бот для завантаження відео та аудіо з YouTube.\n\n"
            f"📋 Що я вмію:\n"
            f"• 📥 Завантажувати відео у різних якостях\n"
            f"• 🎵 Витягувати аудіо у форматі MP3\n"
            f"• ⚙️ Налаштовувати якість завантаження\n"
            f"• 📊 Показувати прогрес завантаження\n"
            f"• 📋 Зберігати історію завантажень\n\n"
            f"🚀 Виберіть дію в меню або просто надішліть посилання на YouTube відео!"
        )
        
        await message.answer(
            welcome_text,
            reply_markup=MainKeyboard.get_main_menu()
        )
        
    except Exception as e:
        await message.answer(
            "❌ Виникла помилка при запуску бота. Спробуйте ще раз.",
            reply_markup=MainKeyboard.get_main_menu()
        )


@router.message(Command("help"))
async def help_command(message: Message):
    """Обробка команди /help"""
    help_text = (
        "ℹ️ **Допомога по використанню бота**\n\n"
        "🎬 **Як завантажити відео:**\n"
        "1. Натисніть кнопку '📥 Завантажити відео'\n"
        "2. Надішліть посилання на YouTube відео\n"
        "3. Виберіть якість відео\n"
        "4. Дочекайтеся завершення завантаження\n\n"
        
        "🎵 **Як завантажити аудіо:**\n"
        "1. Натисніть кнопку '🎵 Завантажити аудіо'\n"
        "2. Надішліть посилання на YouTube відео\n"
        "3. Виберіть якість аудіо\n"
        "4. Отримайте MP3 файл\n\n"
        
        "📋 **Додаткові можливості:**\n"
        "• Переглядайте історію завантажень\n"
        "• Налаштовуйте якість за замовчуванням\n"
        "• Переглядайте статистику використання\n\n"
        
        "⚠️ **Обмеження:**\n"
        f"• Максимальна тривалість відео: 60 хвилин\n"
        f"• Максимальний розмір файлу: 50 МБ\n"
        f"• Максимум завантажень за годину: 10\n\n"
        
        "❓ Якщо у вас виникли питання, зверніться до адміністратора."
    )
    
    await message.answer(
        help_text,
        parse_mode="Markdown",
        reply_markup=MainKeyboard.get_help_keyboard()
    )


@router.message(F.text == "ℹ️ Допомога")
async def help_button(message: Message):
    """Обробка кнопки допомоги"""
    await help_command(message)


@router.message(F.text == "🏠 Головне меню")
async def main_menu_button(message: Message, state: FSMContext):
    """Обробка кнопки головного меню"""
    await state.clear()
    
    await message.answer(
        "🏠 Головне меню",
        reply_markup=MainKeyboard.get_main_menu()
    )


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Обробка callback головного меню"""
    await state.clear()
    
    try:
        await callback.message.edit_text(
            "🏠 Головне меню\n\nВиберіть дію:",
            reply_markup=MainKeyboard.get_back_to_menu()
        )
    except:
        await callback.message.answer(
            "🏠 Головне меню",
            reply_markup=MainKeyboard.get_main_menu()
        )
    
    await callback.answer()


@router.message(F.text == "📊 Статистика")
async def statistics_button(message: Message):
    """Обробка кнопки статистики"""
    try:
        async for session in get_async_session():
            user_repo = UserRepository(session)
            
            # Отримуємо користувача
            user = await user_repo.get_by_telegram_id(message.from_user.id)
            if not user:
                await message.answer("❌ Користувача не знайдено.")
                return
            
            # Формуємо статистику
            stats_text = (
                f"📊 **Ваша статистика**\n\n"
                f"👤 **Профіль:**\n"
                f"• ID: {user.telegram_id}\n"
                f"• Ім'я: {user.first_name or 'Не вказано'}\n"
                f"• Username: @{user.username or 'Не вказано'}\n"
                f"• Дата реєстрації: {user.created_at.strftime('%d.%m.%Y')}\n\n"
                
                f"📥 **Завантаження:**\n"
                f"• Всього завантажень: {user.total_downloads}\n"
                f"• Завантажень сьогодні: {user.downloads_today}\n"
                f"• Останнє завантаження: {user.last_download_date.strftime('%d.%m.%Y %H:%M') if user.last_download_date else 'Немає'}\n\n"
                
                f"⚙️ **Налаштування:**\n"
                f"• Якість відео: {user.preferred_quality}\n"
                f"• Формат: {user.preferred_format}\n"
                f"• Мова: {user.language_code.upper()}"
            )
            
            await message.answer(
                stats_text,
                parse_mode="Markdown",
                reply_markup=MainKeyboard.get_back_to_menu()
            )
            break
            
    except Exception as e:
        await message.answer(
            "❌ Помилка отримання статистики. Спробуйте пізніше.",
            reply_markup=MainKeyboard.get_back_to_menu()
        )


@router.message(F.text == "❌ Скасувати")
async def cancel_button(message: Message, state: FSMContext):
    """Обробка кнопки скасування"""
    await state.clear()
    
    await message.answer(
        "❌ Дію скасовано.",
        reply_markup=MainKeyboard.get_main_menu()
    )


@router.callback_query(F.data.startswith("help_"))
async def help_callback(callback: CallbackQuery):
    """Обробка callback допомоги"""
    help_type = callback.data.split("_")[1]
    
    help_texts = {
        "video": (
            "📥 **Завантаження відео**\n\n"
            "1. Натисніть кнопку '📥 Завантажити відео'\n"
            "2. Надішліть посилання на YouTube відео\n"
            "3. Переглянете інформацію про відео\n"
            "4. Виберіть якість (360p, 480p, 720p, 1080p)\n"
            "5. Дочекайтеся завершення завантаження\n"
            "6. Отримайте відео файл\n\n"
            "⚠️ Максимальна тривалість: 60 хвилин\n"
            "⚠️ Максимальний розмір: 50 МБ"
        ),
        "audio": (
            "🎵 **Завантаження аудіо**\n\n"
            "1. Натисніть кнопку '🎵 Завантажити аудіо'\n"
            "2. Надішліть посилання на YouTube відео\n"
            "3. Переглянете інформацію про відео\n"
            "4. Виберіть якість аудіо (128, 192, 256, 320 kbps)\n"
            "5. Дочекайтеся конвертації в MP3\n"
            "6. Отримайте аудіо файл\n\n"
            "ℹ️ Формат: MP3\n"
            "ℹ️ Якість: до 320 kbps"
        ),
        "settings": (
            "⚙️ **Налаштування**\n\n"
            "У розділі налаштувань ви можете:\n\n"
            "• Встановити якість відео за замовчуванням\n"
            "• Вибрати формат файлів\n"
            "• Змінити мову інтерфейсу\n"
            "• Переглянути інформацію про акаунт\n"
            "• Очистити історію завантажень\n\n"
            "Налаштування зберігаються автоматично."
        ),
        "faq": (
            "❓ **Часті питання**\n\n"
            "**Q: Чому відео не завантажується?**\n"
            "A: Перевірте посилання та доступність відео\n\n"
            "**Q: Скільки часу займає завантаження?**\n"
            "A: Залежить від розміру файлу (зазвичай 1-5 хвилин)\n\n"
            "**Q: Які формати підтримуються?**\n"
            "A: Відео: MP4, WebM; Аудіо: MP3\n\n"
            "**Q: Є ліміти на завантаження?**\n"
            "A: Так, до 10 файлів на годину на користувача\n\n"
            "**Q: Бот не відповідає?**\n"
            "A: Спробуйте команду /start"
        )
    }
    
    text = help_texts.get(help_type, "❌ Розділ допомоги не знайдено")
    
    try:
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=MainKeyboard.get_help_keyboard()
        )
    except:
        await callback.message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=MainKeyboard.get_help_keyboard()
        )
    
    await callback.answer()