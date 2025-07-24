from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class MainKeyboard:
    """Основні клавіатури бота"""
    
    @staticmethod
    def get_main_menu() -> ReplyKeyboardMarkup:
        """Головне меню"""
        builder = ReplyKeyboardBuilder()
        
        # Основні функції
        builder.row(
            KeyboardButton(text="📥 Завантажити відео"),
            KeyboardButton(text="🎵 Завантажити аудіо")
        )
        
        builder.row(
            KeyboardButton(text="📋 Мої завантаження"),
            KeyboardButton(text="⚙️ Налаштування")
        )
        
        builder.row(
            KeyboardButton(text="ℹ️ Допомога"),
            KeyboardButton(text="📊 Статистика")
        )
        
        return builder.as_markup(
            resize_keyboard=True,
            one_time_keyboard=False,
            input_field_placeholder="Виберіть дію або надішліть посилання на YouTube..."
        )
    
    @staticmethod
    def get_cancel_keyboard() -> ReplyKeyboardMarkup:
        """Клавіатура для скасування"""
        builder = ReplyKeyboardBuilder()
        builder.add(KeyboardButton(text="❌ Скасувати"))
        
        return builder.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    
    @staticmethod
    def get_back_to_menu() -> InlineKeyboardMarkup:
        """Кнопка повернення до меню"""
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="🏠 Головне меню",
            callback_data="main_menu"
        ))
        
        return builder.as_markup()
    
    @staticmethod
    def get_url_input_keyboard() -> ReplyKeyboardMarkup:
        """Клавіатура для введення URL"""
        builder = ReplyKeyboardBuilder()
        
        builder.row(KeyboardButton(text="❌ Скасувати"))
        builder.row(KeyboardButton(text="📋 Вставити з буфера"))
        
        return builder.as_markup(
            resize_keyboard=True,
            one_time_keyboard=False,
            input_field_placeholder="Надішліть посилання на YouTube відео..."
        )
    
    @staticmethod
    def get_help_keyboard() -> InlineKeyboardMarkup:
        """Клавіатура допомоги"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📥 Як завантажити відео?", callback_data="help_video"),
            InlineKeyboardButton(text="🎵 Як завантажити аудіо?", callback_data="help_audio")
        )
        
        builder.row(
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="help_settings"),
            InlineKeyboardButton(text="❓ FAQ", callback_data="help_faq")
        )
        
        builder.row(
            InlineKeyboardButton(text="🏠 Головне меню", callback_data="main_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def get_confirmation_keyboard(action: str, video_id: str = None) -> InlineKeyboardMarkup:
        """Клавіатура підтвердження дії"""
        builder = InlineKeyboardBuilder()
        
        confirm_data = f"confirm_{action}"
        cancel_data = f"cancel_{action}"
        
        if video_id:
            confirm_data += f"_{video_id}"
            cancel_data += f"_{video_id}"
        
        builder.row(
            InlineKeyboardButton(text="✅ Підтвердити", callback_data=confirm_data),
            InlineKeyboardButton(text="❌ Скасувати", callback_data=cancel_data)
        )
        
        return builder.as_markup()
    
    @staticmethod
    def get_admin_keyboard() -> InlineKeyboardMarkup:
        """Адміністративна клавіатура"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="👥 Користувачі", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        )
        
        builder.row(
            InlineKeyboardButton(text="📥 Завантаження", callback_data="admin_downloads"),
            InlineKeyboardButton(text="🗂 Логи", callback_data="admin_logs")
        )
        
        builder.row(
            InlineKeyboardButton(text="⚙️ Налаштування", callback_data="admin_settings"),
            InlineKeyboardButton(text="🔄 Перезапуск", callback_data="admin_restart")
        )
        
        builder.row(
            InlineKeyboardButton(text="🏠 Головне меню", callback_data="main_menu")
        )
        
        return builder.as_markup()