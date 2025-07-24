from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional
from downloader.models.video_info import VideoInfo


class DownloadKeyboard:
    """Клавіатури для завантажень"""
    
    @staticmethod
    def get_video_info_keyboard(video_info: VideoInfo) -> InlineKeyboardMarkup:
        """Клавіатура з інформацією про відео"""
        builder = InlineKeyboardBuilder()
        
        # Кнопки завантаження
        builder.row(
            InlineKeyboardButton(
                text="📥 Завантажити відео",
                callback_data=f"download_video_{video_info.id}"
            ),
            InlineKeyboardButton(
                text="🎵 Завантажити аудіо",
                callback_data=f"download_audio_{video_info.id}"
            )
        )
        
        # Кнопка налаштувань якості
        builder.row(
            InlineKeyboardButton(
                text="⚙️ Вибрати якість",
                callback_data=f"quality_settings_{video_info.id}"
            )
        )
        
        # Кнопка скасування
        builder.row(
            InlineKeyboardButton(
                text="❌ Скасувати",
                callback_data="cancel_download"
            )
        )
        
        return builder.as_markup()
    
    @staticmethod
    def get_quality_selection_keyboard(video_info: VideoInfo, download_type: str) -> InlineKeyboardMarkup:
        """Клавіатура вибору якості"""
        builder = InlineKeyboardBuilder()
        
        if download_type == "video":
            # Доступні якості відео
            qualities = ["360p", "480p", "720p", "1080p"]
            for quality in qualities:
                if any(f.height and f.height <= int(quality[:-1]) for f in video_info.video_formats):
                    builder.row(
                        InlineKeyboardButton(
                            text=f"📹 {quality}",
                            callback_data=f"select_video_quality_{video_info.id}_{quality}"
                        )
                    )
        
        elif download_type == "audio":
            # Доступні якості аудіо
            qualities = ["128", "192", "256", "320"]
            for quality in qualities:
                builder.row(
                    InlineKeyboardButton(
                        text=f"🎵 {quality} kbps",
                        callback_data=f"select_audio_quality_{video_info.id}_{quality}"
                    )
                )
        
        # Кнопка назад
        builder.row(
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"back_to_video_{video_info.id}"
            )
        )
        
        return builder.as_markup()
    
    @staticmethod
    def get_download_progress_keyboard(download_id: int, can_cancel: bool = True) -> InlineKeyboardMarkup:
        """Клавіатура для прогресу завантаження"""
        builder = InlineKeyboardBuilder()
        
        if can_cancel:
            builder.row(
                InlineKeyboardButton(
                    text="⏹ Зупинити завантаження",
                    callback_data=f"cancel_download_{download_id}"
                )
            )
        
        # Кнопка оновлення прогресу
        builder.row(
            InlineKeyboardButton(
                text="🔄 Оновити",
                callback_data=f"refresh_progress_{download_id}"
            )
        )
        
        return builder.as_markup()
    
    @staticmethod
    def get_download_completed_keyboard(download_id: int, has_file: bool = True) -> InlineKeyboardMarkup:
        """Клавіатура для завершеного завантаження"""
        builder = InlineKeyboardBuilder()
        
        if has_file:
            builder.row(
                InlineKeyboardButton(
                    text="📤 Надіслати файл",
                    callback_data=f"send_file_{download_id}"
                )
            )
        
        builder.row(
            InlineKeyboardButton(
                text="🗑 Видалити запис",
                callback_data=f"delete_download_{download_id}"
            )
        )
        
        builder.row(
            InlineKeyboardButton(
                text="🏠 Головне меню",
                callback_data="main_menu"
            )
        )
        
        return builder.as_markup()
    
    @staticmethod
    def get_downloads_list_keyboard(downloads: List[dict], page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
        """Клавіатура зі списком завантажень"""
        builder = InlineKeyboardBuilder()
        
        # Показуємо завантаження для поточної сторінки
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_downloads = downloads[start_idx:end_idx]
        
        for download in page_downloads:
            status_emoji = {
                'completed': '✅',
                'downloading': '⏳',
                'pending': '⏸',
                'failed': '❌',
                'cancelled': '⏹'
            }.get(download['status'], '❓')
            
            title = download['title'][:30] + "..." if len(download['title']) > 30 else download['title']
            
            builder.row(
                InlineKeyboardButton(
                    text=f"{status_emoji} {title}",
                    callback_data=f"download_info_{download['id']}"
                )
            )
        
        # Навігація по сторінках
        nav_buttons = []
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="◀️ Попередня",
                    callback_data=f"downloads_page_{page - 1}"
                )
            )
        
        if end_idx < len(downloads):
            nav_buttons.append(
                InlineKeyboardButton(
                    text="Наступна ▶️",
                    callback_data=f"downloads_page_{page + 1}"
                )
            )
        
        if nav_buttons:
            builder.row(*nav_buttons)
        
        # Кнопка оновлення списку
        builder.row(
            InlineKeyboardButton(
                text="🔄 Оновити список",
                callback_data="refresh_downloads"
            )
        )
        
        # Кнопка головного меню
        builder.row(
            InlineKeyboardButton(
                text="🏠 Головне меню",
                callback_data="main_menu"
            )
        )
        
        return builder.as_markup()
    
    @staticmethod
    def get_download_actions_keyboard(download_id: int, status: str) -> InlineKeyboardMarkup:
        """Клавіатура дій для конкретного завантаження"""
        builder = InlineKeyboardBuilder()
        
        if status == "completed":
            builder.row(
                InlineKeyboardButton(
                    text="📤 Надіслати файл",
                    callback_data=f"send_file_{download_id}"
                )
            )
        
        elif status in ["pending", "downloading"]:
            builder.row(
                InlineKeyboardButton(
                    text="⏹ Скасувати",
                    callback_data=f"cancel_download_{download_id}"
                )
            )
        
        elif status == "failed":
            builder.row(
                InlineKeyboardButton(
                    text="🔄 Спробувати знову",
                    callback_data=f"retry_download_{download_id}"
                )
            )
        
        # Загальні дії
        builder.row(
            InlineKeyboardButton(
                text="🗑 Видалити",
                callback_data=f"delete_download_{download_id}"
            ),
            InlineKeyboardButton(
                text="📋 Деталі",
                callback_data=f"download_details_{download_id}"
            )
        )
        
        builder.row(
            InlineKeyboardButton(
                text="◀️ До списку",
                callback_data="my_downloads"
            )
        )
        
        return builder.as_markup()
    
    @staticmethod
    def get_bulk_actions_keyboard() -> InlineKeyboardMarkup:
        """Клавіатура масових дій"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(
                text="🗑 Очистити завершені",
                callback_data="bulk_clear_completed"
            ),
            InlineKeyboardButton(
                text="⏹ Скасувати всі",
                callback_data="bulk_cancel_all"
            )
        )
        
        builder.row(
            InlineKeyboardButton(
                text="❌ Скасувати",
                callback_data="cancel_bulk_actions"
            )
        )
        
        return builder.as_markup()