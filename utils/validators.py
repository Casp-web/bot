import re
import validators
from typing import Optional
from urllib.parse import urlparse, parse_qs


class URLValidator:
    """Валідатор для URL"""
    
    YOUTUBE_DOMAINS = [
        'youtube.com',
        'www.youtube.com',
        'm.youtube.com',
        'music.youtube.com',
        'youtu.be',
        'www.youtu.be'
    ]
    
    YOUTUBE_PATTERNS = [
        # Стандартні watch URL
        r'(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})(?:[&\s#]|$)',
        r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})(?:[/?\s#]|$)',
        r'(?:youtube\.com/v/)([a-zA-Z0-9_-]{11})(?:[/?\s#]|$)',
        
        # YouTube Shorts
        r'(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})(?:[/?\s#]|$)',
        
        # YouTube Music
        r'(?:music\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})(?:[&\s#]|$)',
        
        # Мобільні версії
        r'(?:m\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})(?:[&\s#]|$)',
        
        # youtu.be короткі посилання
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})(?:[?\s#]|$)',
        
        # Інші можливі формати з параметром v=
        r'youtube\.com/.*[?&]v=([a-zA-Z0-9_-]{11})(?:[&\s#]|$)',
    ]
    
    def is_valid_url(self, url: str) -> bool:
        """Перевірка чи є URL валідним"""
        try:
            return validators.url(url) is True
        except Exception:
            return False
    
    def is_valid_youtube_url(self, url: str) -> bool:
        """Перевірка чи є URL валідним YouTube посиланням"""
        if not url or not isinstance(url, str):
            return False
        
        # Очищуємо URL від пробілів
        url = url.strip()
        
        # Базова перевірка URL
        if not self.is_valid_url(url):
            return False
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Перевірка домену
            if not any(yt_domain in domain for yt_domain in self.YOUTUBE_DOMAINS):
                return False
            
            # Перевірка патернів та отримання video_id
            video_id = self.extract_video_id(url)
            return video_id is not None
            
        except Exception:
            return False
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Витягнути ID відео з YouTube URL"""
        if not url or not isinstance(url, str):
            return None
        
        # Очищуємо URL від пробілів
        url = url.strip()
        
        for pattern in self.YOUTUBE_PATTERNS:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                video_id = match.group(1)
                
                # Валідуємо довжину ID (YouTube ID завжди 11 символів)
                if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', video_id):
                    return video_id
        
        return None
    
    def normalize_youtube_url(self, url: str) -> Optional[str]:
        """Нормалізація YouTube URL до стандартного формату"""
        video_id = self.extract_video_id(url)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        return None


class TextValidator:
    """Валідатор для тексту"""
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Перевірка чи безпечне ім'я файлу"""
        if not filename or len(filename) > 255:
            return False
        
        # Заборонені символи для імен файлів
        forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        return not any(char in filename for char in forbidden_chars)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Очищення імені файлу від небезпечних символів"""
        if not filename:
            return "untitled"
        
        # Замінюємо заборонені символи
        forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in forbidden_chars:
            filename = filename.replace(char, '_')
        
        # Обмежуємо довжину
        if len(filename) > 200:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            max_name_length = 200 - len(ext) - 1 if ext else 200
            filename = name[:max_name_length] + ('.' + ext if ext else '')
        
        return filename.strip()
    
    @staticmethod
    def is_valid_quality(quality: str, quality_type: str = "video") -> bool:
        """Перевірка валідності якості"""
        if quality_type == "video":
            valid_qualities = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
            return quality in valid_qualities
        elif quality_type == "audio":
            try:
                bitrate = int(quality)
                return 64 <= bitrate <= 320
            except ValueError:
                return False
        return False


class UserInputValidator:
    """Валідатор для користувацького вводу"""
    
    @staticmethod
    def is_valid_telegram_id(telegram_id: int) -> bool:
        """Перевірка валідності Telegram ID"""
        return isinstance(telegram_id, int) and telegram_id > 0
    
    @staticmethod
    def is_valid_message_length(message: str, max_length: int = 4096) -> bool:
        """Перевірка довжини повідомлення"""
        return isinstance(message, str) and len(message) <= max_length
    
    @staticmethod
    def sanitize_user_input(text: str) -> str:
        """Очищення користувацького вводу"""
        if not isinstance(text, str):
            return ""
        
        # Видаляємо потенційно небезпечні символи
        text = re.sub(r'[<>]', '', text)
        
        # Обмежуємо довжину
        if len(text) > 1000:
            text = text[:1000]
        
        return text.strip()