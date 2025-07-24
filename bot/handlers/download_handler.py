from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.main_keyboard import MainKeyboard

router = Router()


class DownloadStates(StatesGroup):
    waiting_for_video_url = State()
    waiting_for_audio_url = State()


@router.message(F.text == "📥 Завантажити відео")
async def download_video_button(message: Message, state: FSMContext):
    """Обробка кнопки завантаження відео"""
    await state.set_state(DownloadStates.waiting_for_video_url)
    
    await message.answer(
        "📥 **Завантаження відео**\n\n"
        "Надішліть посилання на YouTube відео, яке хочете завантажити.\n\n"
        "Приклади посилань:\n"
        "• https://www.youtube.com/watch?v=VIDEO_ID\n"
        "• https://youtu.be/VIDEO_ID\n"
        "• https://youtube.com/embed/VIDEO_ID",
        parse_mode="Markdown",
        reply_markup=MainKeyboard.get_url_input_keyboard()
    )


@router.message(F.text == "🎵 Завантажити аудіо")
async def download_audio_button(message: Message, state: FSMContext):
    """Обробка кнопки завантаження аудіо"""
    await state.set_state(DownloadStates.waiting_for_audio_url)
    
    await message.answer(
        "🎵 **Завантаження аудіо**\n\n"
        "Надішліть посилання на YouTube відео, з якого хочете витягти аудіо.\n\n"
        "Аудіо буде конвертовано у формат MP3 з обраною якістю.\n\n"
        "Приклади посилань:\n"
        "• https://www.youtube.com/watch?v=VIDEO_ID\n"
        "• https://youtu.be/VIDEO_ID",
        parse_mode="Markdown",
        reply_markup=MainKeyboard.get_url_input_keyboard()
    )


@router.message(F.text == "📋 Мої завантаження")
async def my_downloads_button(message: Message):
    """Обробка кнопки моїх завантажень"""
    await message.answer(
        "📋 **Мої завантаження**\n\n"
        "Функція перегляду завантажень буде доступна незабаром.\n"
        "Тут ви зможете переглядати історію своїх завантажень, "
        "їх статус та керувати файлами.",
        parse_mode="Markdown",
        reply_markup=MainKeyboard.get_back_to_menu()
    )


@router.message(F.text == "⚙️ Налаштування")
async def settings_button(message: Message):
    """Обробка кнопки налаштувань"""
    await message.answer(
        "⚙️ **Налаштування**\n\n"
        "Функція налаштувань буде доступна незабаром.\n"
        "Тут ви зможете:\n\n"
        "• Встановити якість відео за замовчуванням\n"
        "• Вибрати якість аудіо\n"
        "• Змінити формат файлів\n"
        "• Налаштувати мову інтерфейсу\n"
        "• Керувати сповіщеннями",
        parse_mode="Markdown",
        reply_markup=MainKeyboard.get_back_to_menu()
    )


@router.message(DownloadStates.waiting_for_video_url)
async def process_video_url(message: Message, state: FSMContext):
    """Обробка URL для завантаження відео"""
    # Очищуємо стан, URL буде оброблено в url_handler
    await state.clear()
    
    # Додаємо тип завантаження до стану
    await state.update_data(download_type="video")


@router.message(DownloadStates.waiting_for_audio_url)
async def process_audio_url(message: Message, state: FSMContext):
    """Обробка URL для завантаження аудіо"""
    # Очищуємо стан, URL буде оброблено в url_handler
    await state.clear()
    
    # Додаємо тип завантаження до стану
    await state.update_data(download_type="audio")