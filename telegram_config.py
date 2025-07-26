import os
import json
from typing import Optional

class TelegramConfig:
    """Клас для роботи з конфігурацією Telegram клієнта"""
    
    def __init__(self, config_file: str = "telegram_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Завантаження конфігурації з файлу"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save_config(self) -> None:
        """Збереження конфігурації у файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Отримання значення з конфігурації"""
        return self.config.get(key, default)
    
    def set(self, key: str, value) -> None:
        """Встановлення значення в конфігурації"""
        self.config[key] = value
        self.save_config()
    
    def get_api_id(self) -> Optional[str]:
        """Отримання API ID"""
        return self.get('api_id')
    
    def set_api_id(self, api_id: str) -> None:
        """Встановлення API ID"""
        self.set('api_id', api_id)
    
    def get_api_hash(self) -> Optional[str]:
        """Отримання API Hash"""
        return self.get('api_hash')
    
    def set_api_hash(self, api_hash: str) -> None:
        """Встановлення API Hash"""
        self.set('api_hash', api_hash)
    
    def get_phone(self) -> Optional[str]:
        """Отримання номеру телефону"""
        return self.get('phone')
    
    def set_phone(self, phone: str) -> None:
        """Встановлення номеру телефону"""
        self.set('phone', phone)
    
    def get_session_name(self) -> str:
        """Отримання імені сесії"""
        return self.get('session_name', 'telegram_session')
    
    def set_session_name(self, session_name: str) -> None:
        """Встановлення імені сесії"""
        self.set('session_name', session_name)
    
    def get_theme(self) -> str:
        """Отримання теми"""
        return self.get('theme', 'light')
    
    def set_theme(self, theme: str) -> None:
        """Встановлення теми"""
        self.set('theme', theme)
    
    def get_font_size(self) -> int:
        """Отримання розміру шрифту"""
        return self.get('font_size', 10)
    
    def set_font_size(self, font_size: int) -> None:
        """Встановлення розміру шрифту"""
        self.set('font_size', font_size)
    
    def get_window_geometry(self) -> str:
        """Отримання розміру та позиції вікна"""
        return self.get('window_geometry', '1200x800')
    
    def set_window_geometry(self, geometry: str) -> None:
        """Встановлення розміру та позиції вікна"""
        self.set('window_geometry', geometry)