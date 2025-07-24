from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, update, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from database.models.download import Download
from database.models.user import User
from .base_repository import BaseRepository


class DownloadRepository(BaseRepository[Download]):
    def __init__(self, session: AsyncSession):
        super().__init__(Download, session)
    
    async def create_download(self, user_id: int, youtube_url: str, video_id: str, 
                            download_type: str, **kwargs) -> Download:
        """Створення нового завантаження"""
        download = await self.create(
            user_id=user_id,
            youtube_url=youtube_url,
            video_id=video_id,
            download_type=download_type,
            **kwargs
        )
        return download
    
    async def get_by_video_id(self, video_id: str, user_id: int = None) -> Optional[Download]:
        """Отримання завантаження за ID відео"""
        query = select(Download).where(Download.video_id == video_id)
        if user_id:
            query = query.where(Download.user_id == user_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_downloads(self, user_id: int, limit: int = 10, 
                               offset: int = 0) -> List[Download]:
        """Отримання завантажень користувача"""
        result = await self.session.execute(
            select(Download)
            .where(Download.user_id == user_id)
            .order_by(desc(Download.created_at))
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_active_downloads(self, user_id: int = None) -> List[Download]:
        """Отримання активних завантажень"""
        query = select(Download).where(
            Download.status.in_(["pending", "downloading"])
        )
        if user_id:
            query = query.where(Download.user_id == user_id)
        
        result = await self.session.execute(query.order_by(Download.created_at))
        return result.scalars().all()
    
    async def update_download_status(self, download_id: int, status: str, 
                                   progress: int = None, error_message: str = None) -> bool:
        """Оновлення статусу завантаження"""
        update_data = {"status": status}
        
        if progress is not None:
            update_data["progress"] = progress
        
        if error_message:
            update_data["error_message"] = error_message
        
        if status == "downloading" and not await self.get_started_time(download_id):
            update_data["started_at"] = datetime.utcnow()
        elif status == "completed":
            update_data["completed_at"] = datetime.utcnow()
            update_data["progress"] = 100
        
        result = await self.session.execute(
            update(Download)
            .where(Download.id == download_id)
            .values(**update_data)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_started_time(self, download_id: int) -> Optional[datetime]:
        """Отримання часу початку завантаження"""
        result = await self.session.execute(
            select(Download.started_at).where(Download.id == download_id)
        )
        return result.scalar()
    
    async def update_file_info(self, download_id: int, file_path: str = None, 
                             telegram_file_id: str = None, file_size: float = None) -> bool:
        """Оновлення інформації про файл"""
        update_data = {}
        if file_path:
            update_data["file_path"] = file_path
        if telegram_file_id:
            update_data["telegram_file_id"] = telegram_file_id
        if file_size:
            update_data["file_size"] = file_size
        
        if not update_data:
            return False
        
        result = await self.session.execute(
            update(Download)
            .where(Download.id == download_id)
            .values(**update_data)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_downloads_by_status(self, status: str, limit: int = 100) -> List[Download]:
        """Отримання завантажень за статусом"""
        result = await self.session.execute(
            select(Download)
            .where(Download.status == status)
            .order_by(Download.created_at)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def cleanup_old_downloads(self, days: int = 7) -> int:
        """Очищення старих завантажень"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            update(Download)
            .where(
                Download.created_at < cutoff_date,
                Download.status.in_(["completed", "failed", "cancelled"])
            )
            .values(file_path=None)
        )
        await self.session.commit()
        return result.rowcount
    
    async def get_user_downloads_count_today(self, user_id: int) -> int:
        """Отримання кількості завантажень користувача за сьогодні"""
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        
        result = await self.session.execute(
            select(func.count(Download.id))
            .where(
                Download.user_id == user_id,
                Download.created_at >= today,
                Download.created_at < tomorrow
            )
        )
        return result.scalar()
    
    async def get_downloads_stats(self) -> dict:
        """Отримання статистики завантажень"""
        total = await self.session.execute(select(func.count(Download.id)))
        completed = await self.session.execute(
            select(func.count(Download.id)).where(Download.status == "completed")
        )
        failed = await self.session.execute(
            select(func.count(Download.id)).where(Download.status == "failed")
        )
        active = await self.session.execute(
            select(func.count(Download.id))
            .where(Download.status.in_(["pending", "downloading"]))
        )
        
        return {
            "total": total.scalar(),
            "completed": completed.scalar(),
            "failed": failed.scalar(),
            "active": active.scalar()
        }