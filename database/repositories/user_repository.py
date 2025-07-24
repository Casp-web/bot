from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User
from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Отримання користувача за Telegram ID"""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def create_or_update_user(self, telegram_id: int, **kwargs) -> User:
        """Створення або оновлення користувача"""
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            # Оновлюємо існуючого користувача
            for key, value in kwargs.items():
                setattr(user, key, value)
            user.last_seen = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(user)
        else:
            # Створюємо нового користувача
            user = await self.create(telegram_id=telegram_id, **kwargs)
        return user
    
    async def update_last_seen(self, telegram_id: int) -> bool:
        """Оновлення часу останньої активності"""
        result = await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(last_seen=datetime.utcnow())
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def increment_downloads(self, telegram_id: int) -> bool:
        """Збільшення лічильника завантажень"""
        today = datetime.utcnow().date()
        result = await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(
                total_downloads=User.total_downloads + 1,
                downloads_today=User.downloads_today + 1,
                last_download_date=datetime.utcnow()
            )
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def reset_daily_downloads(self) -> int:
        """Скидання денного лічильника завантажень"""
        result = await self.session.execute(
            update(User).values(downloads_today=0)
        )
        await self.session.commit()
        return result.rowcount
    
    async def get_user_downloads_today(self, telegram_id: int) -> int:
        """Отримання кількості завантажень користувача за сьогодні"""
        result = await self.session.execute(
            select(User.downloads_today)
            .where(User.telegram_id == telegram_id)
        )
        count = result.scalar()
        return count or 0
    
    async def ban_user(self, telegram_id: int, reason: str = None) -> bool:
        """Блокування користувача"""
        result = await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(is_banned=True, ban_reason=reason)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def unban_user(self, telegram_id: int) -> bool:
        """Розблокування користувача"""
        result = await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(is_banned=False, ban_reason=None)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_active_users_count(self) -> int:
        """Отримання кількості активних користувачів"""
        result = await self.session.execute(
            select(func.count(User.id))
            .where(User.is_active == True, User.is_banned == False)
        )
        return result.scalar()
    
    async def get_users_stats(self) -> dict:
        """Отримання статистики користувачів"""
        total_users = await self.session.execute(select(func.count(User.id)))
        active_users = await self.session.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        banned_users = await self.session.execute(
            select(func.count(User.id)).where(User.is_banned == True)
        )
        
        return {
            "total": total_users.scalar(),
            "active": active_users.scalar(),
            "banned": banned_users.scalar()
        }