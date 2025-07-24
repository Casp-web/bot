from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class Download(Base):
    __tablename__ = "downloads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Інформація про відео
    youtube_url = Column(String(500), nullable=False)
    video_id = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # в секундах
    thumbnail_url = Column(String(500), nullable=True)
    
    # Параметри завантаження
    download_type = Column(String(20), nullable=False)  # 'video' або 'audio'
    quality = Column(String(50), nullable=True)
    format = Column(String(20), nullable=True)
    file_size = Column(Float, nullable=True)  # в МБ
    
    # Статус завантаження
    status = Column(String(50), default="pending")  # pending, downloading, completed, failed, cancelled
    progress = Column(Integer, default=0)  # відсоток завершення
    error_message = Column(Text, nullable=True)
    
    # Файлова інформація
    file_path = Column(String(500), nullable=True)
    telegram_file_id = Column(String(200), nullable=True)
    
    # Дати
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Зв'язки
    user = relationship("User", backref="downloads")
    
    def __repr__(self):
        return f"<Download(id={self.id}, video_id={self.video_id}, status={self.status})>"