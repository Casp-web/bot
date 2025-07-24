import os
import re
import asyncio
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import yt_dlp
from loguru import logger

from config.settings.base import settings
from downloader.models.video_info import VideoInfo, VideoFormat
from utils.validators import URLValidator


class YouTubeService:
    """Сервіс для роботи з YouTube через yt-dlp"""
    
    def __init__(self):
        self.url_validator = URLValidator()
        self._setup_directories()
    
    def _setup_directories(self):
        """Створення необхідних директорій"""
        Path(settings.DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True)
        Path(settings.TEMP_PATH).mkdir(parents=True, exist_ok=True)
    
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """Отримання інформації про відео"""
        try:
            if not self.url_validator.is_valid_youtube_url(url):
                raise ValueError("Невірне посилання на YouTube")
            
            # Налаштування yt-dlp для отримання інформації
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
            }
            
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None, self._extract_info, url, ydl_opts
            )
            
            if not info:
                return None
            
            return self._parse_video_info(info)
            
        except Exception as e:
            logger.error(f"Помилка отримання інформації про відео {url}: {e}")
            return None
    
    def _extract_info(self, url: str, ydl_opts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Синхронне отримання інформації через yt-dlp"""
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            logger.error(f"yt-dlp помилка: {e}")
            return None
    
    def _parse_video_info(self, info: Dict[str, Any]) -> VideoInfo:
        """Парсинг інформації про відео"""
        # Парсинг форматів
        formats = []
        video_formats = []
        audio_formats = []
        
        for fmt in info.get('formats', []):
            video_format = VideoFormat(
                format_id=fmt.get('format_id', ''),
                ext=fmt.get('ext', ''),
                quality=fmt.get('quality', ''),
                filesize=fmt.get('filesize'),
                filesize_approx=fmt.get('filesize_approx'),
                vcodec=fmt.get('vcodec'),
                acodec=fmt.get('acodec'),
                fps=fmt.get('fps'),
                height=fmt.get('height'),
                width=fmt.get('width'),
                tbr=fmt.get('tbr'),
                abr=fmt.get('abr'),
                vbr=fmt.get('vbr')
            )
            
            formats.append(video_format)
            
            # Розподіл на відео та аудіо формати
            if video_format.vcodec and video_format.vcodec != 'none':
                video_formats.append(video_format)
            if video_format.acodec and video_format.acodec != 'none':
                audio_formats.append(video_format)
        
        return VideoInfo(
            id=info.get('id', ''),
            title=info.get('title', ''),
            url=info.get('webpage_url', ''),
            description=info.get('description'),
            duration=info.get('duration'),
            thumbnail=info.get('thumbnail'),
            uploader=info.get('uploader'),
            upload_date=info.get('upload_date'),
            view_count=info.get('view_count'),
            like_count=info.get('like_count'),
            channel=info.get('channel'),
            channel_id=info.get('channel_id'),
            formats=formats,
            video_formats=video_formats,
            audio_formats=audio_formats,
            webpage_url=info.get('webpage_url'),
            original_url=info.get('original_url')
        )
    
    async def download_video(self, url: str, output_path: str, 
                           quality: str = "720p", 
                           progress_callback: Optional[Callable] = None) -> Optional[str]:
        """Завантаження відео"""
        try:
            # Налаштування для завантаження відео
            ydl_opts = {
                'format': self._get_video_format_selector(quality),
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'no_warnings': True,
            }
            
            if progress_callback:
                ydl_opts['progress_hooks'] = [
                    lambda d: self._progress_hook(d, progress_callback)
                ]
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._download_with_ytdl, url, ydl_opts
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Помилка завантаження відео {url}: {e}")
            return None
    
    async def download_audio(self, url: str, output_path: str, 
                           quality: str = "128", 
                           progress_callback: Optional[Callable] = None) -> Optional[str]:
        """Завантаження аудіо"""
        try:
            # Налаштування для завантаження аудіо
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'no_warnings': True,
            }
            
            if progress_callback:
                ydl_opts['progress_hooks'] = [
                    lambda d: self._progress_hook(d, progress_callback)
                ]
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._download_with_ytdl, url, ydl_opts
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Помилка завантаження аудіо {url}: {e}")
            return None
    
    def _download_with_ytdl(self, url: str, ydl_opts: Dict[str, Any]) -> Optional[str]:
        """Синхронне завантаження через yt-dlp"""
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Пошук завантаженого файлу
                if info:
                    filename = ydl.prepare_filename(info)
                    # Для аудіо файлів може змінитися розширення
                    if not os.path.exists(filename):
                        # Пробуємо знайти файл з іншим розширенням
                        base_name = os.path.splitext(filename)[0]
                        for ext in ['.mp3', '.m4a', '.webm', '.mp4']:
                            potential_file = base_name + ext
                            if os.path.exists(potential_file):
                                return potential_file
                    return filename if os.path.exists(filename) else None
                    
        except Exception as e:
            logger.error(f"yt-dlp завантаження помилка: {e}")
            return None
    
    def _get_video_format_selector(self, quality: str) -> str:
        """Отримання селектора формату для відео"""
        quality_map = {
            "144p": "worst[height<=144]",
            "240p": "worst[height<=240]",
            "360p": "best[height<=360]",
            "480p": "best[height<=480]",
            "720p": "best[height<=720]",
            "1080p": "best[height<=1080]",
            "1440p": "best[height<=1440]",
            "2160p": "best[height<=2160]"
        }
        
        return quality_map.get(quality, "best[height<=720]")
    
    def _progress_hook(self, d: Dict[str, Any], callback: Callable):
        """Хук для відстеження прогресу завантаження"""
        try:
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded_bytes = d.get('downloaded_bytes', 0)
                
                if total_bytes > 0:
                    progress = int((downloaded_bytes / total_bytes) * 100)
                    speed = d.get('speed', 0)
                    eta = d.get('eta', 0)
                    
                    callback({
                        'status': 'downloading',
                        'progress': progress,
                        'downloaded_bytes': downloaded_bytes,
                        'total_bytes': total_bytes,
                        'speed': speed,
                        'eta': eta
                    })
            
            elif d['status'] == 'finished':
                callback({
                    'status': 'finished',
                    'progress': 100,
                    'filename': d.get('filename')
                })
                
        except Exception as e:
            logger.error(f"Помилка в progress_hook: {e}")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Витягування ID відео з URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/v/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def is_video_available(self, url: str) -> bool:
        """Перевірка доступності відео"""
        try:
            info = await self.get_video_info(url)
            return info is not None
        except Exception:
            return False
    
    def get_file_size_mb(self, file_path: str) -> float:
        """Отримання розміру файлу в МБ"""
        try:
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                return round(size_bytes / (1024 * 1024), 2)
        except Exception as e:
            logger.error(f"Помилка отримання розміру файлу {file_path}: {e}")
        return 0.0