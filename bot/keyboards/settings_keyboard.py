from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class SettingsKeyboard:
    """Клавіатури для налаштувань"""
    
    @staticmethod
    def get_main_settings() -> InlineKeyboardMarkup:
        """Головне меню налаштувань"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(
                text="🎬 Якість відео",
                callback_data="settings_video_quality"
            ),
            InlineKeyboardButton(
                text="🎵 Якість аудіо",
                callback_data="settings_audio_quality"
            )
        )
        
        builder.row(
            InlineKeyboardButton(
                text="📦 Формат файлів",
                callback_data="settings_format"
            ),
            InlineKeyboardButton(
                text="🌐 Мова",
                callback_data="settings_language"
            )
        )
        
        builder.row(
            InlineKeyboardButton(
                text="🔔 Сповіщення",
                callback_data="settings_notifications"
            ),
            InlineKeyboardButton(
                text="🗑 Очистити історію",
                callback_data="settings_clear_history"
            )
        )
        
        builder.row(
            InlineKeyboardButton(
                text="🏠 Головне меню",
                callback_data="main_menu"
            )
        )
        
        return builder.as_markup()