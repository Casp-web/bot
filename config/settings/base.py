import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from pathlib import Path


class Settings(BaseSettings):
    # Telegram Bot Configuration
    BOT_TOKEN: str
    BOT_NAME: str = "YouTubeDownloaderBot"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./database/bot.db"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Download Configuration
    MAX_FILE_SIZE_MB: int = 50
    DOWNLOAD_PATH: str = "./downloads"
    TEMP_PATH: str = "./temp"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/bot.log"
    
    # YouTube Configuration
    MAX_DURATION_MINUTES: int = 60
    QUALITY_VIDEO: str = "720p"
    QUALITY_AUDIO: str = "128kbps"
    
    # Rate Limiting
    MAX_DOWNLOADS_PER_USER_HOUR: int = 10
    MAX_CONCURRENT_DOWNLOADS: int = 5
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 30
    
    @validator('DOWNLOAD_PATH', 'TEMP_PATH', 'LOG_FILE')
    def create_directories(cls, v):
        path = Path(v)
        if '.' in path.name:  # It's a file
            path.parent.mkdir(parents=True, exist_ok=True)
        else:  # It's a directory
            path.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator('BOT_TOKEN')
    def validate_bot_token(cls, v):
        if not v:
            raise ValueError("BOT_TOKEN must be set")
        # For testing purposes, allow the placeholder token
        if v == "your_telegram_bot_token_here":
            print("WARNING: Using placeholder BOT_TOKEN for testing purposes")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()