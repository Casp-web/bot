from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import timedelta


@dataclass
class VideoFormat:
    """Формат відео/аудіо"""
    format_id: str
    ext: str
    quality: str
    filesize: Optional[int] = None
    filesize_approx: Optional[int] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    fps: Optional[int] = None
    height: Optional[int] = None
    width: Optional[int] = None
    tbr: Optional[float] = None  # total bitrate
    abr: Optional[float] = None  # audio bitrate
    vbr: Optional[float] = None  # video bitrate


@dataclass
class VideoInfo:
    """Інформація про відео з YouTube"""
    id: str
    title: str
    url: str
    description: Optional[str] = None
    duration: Optional[int] = None  # в секундах
    thumbnail: Optional[str] = None
    uploader: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    channel: Optional[str] = None
    channel_id: Optional[str] = None
    
    # Формати
    formats: List[VideoFormat] = None
    video_formats: List[VideoFormat] = None
    audio_formats: List[VideoFormat] = None
    
    # Додаткова інформація
    webpage_url: Optional[str] = None
    original_url: Optional[str] = None
    
    def __post_init__(self):
        if self.formats is None:
            self.formats = []
        if self.video_formats is None:
            self.video_formats = []
        if self.audio_formats is None:
            self.audio_formats = []
    
    @property
    def duration_formatted(self) -> str:
        """Форматована тривалість відео"""
        if not self.duration:
            return "Невідомо"
        
        duration = timedelta(seconds=self.duration)
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def filesize_mb(self) -> Optional[float]:
        """Розмір файлу в МБ (приблизний)"""
        best_format = self.get_best_video_format()
        if best_format and (best_format.filesize or best_format.filesize_approx):
            size = best_format.filesize or best_format.filesize_approx
            return round(size / (1024 * 1024), 2)
        return None
    
    def get_best_video_format(self, max_height: int = 720) -> Optional[VideoFormat]:
        """Отримання найкращого відеоформату"""
        if not self.video_formats:
            return None
        
        # Фільтруємо за максимальною висотою
        suitable_formats = [
            f for f in self.video_formats 
            if f.height and f.height <= max_height
        ]
        
        if not suitable_formats:
            suitable_formats = self.video_formats
        
        # Сортуємо за якістю (висота * fps * bitrate)
        return max(suitable_formats, key=lambda f: (
            f.height or 0,
            f.fps or 0,
            f.tbr or f.vbr or 0
        ))
    
    def get_best_audio_format(self, max_bitrate: int = 128) -> Optional[VideoFormat]:
        """Отримання найкращого аудіоформату"""
        if not self.audio_formats:
            return None
        
        # Фільтруємо за максимальним бітрейтом
        suitable_formats = [
            f for f in self.audio_formats 
            if f.abr and f.abr <= max_bitrate
        ]
        
        if not suitable_formats:
            suitable_formats = self.audio_formats
        
        # Сортуємо за бітрейтом
        return max(suitable_formats, key=lambda f: f.abr or f.tbr or 0)
    
    def get_format_by_id(self, format_id: str) -> Optional[VideoFormat]:
        """Отримання формату за ID"""
        for fmt in self.formats:
            if fmt.format_id == format_id:
                return fmt
        return None