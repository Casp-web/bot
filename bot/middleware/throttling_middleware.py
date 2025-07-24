import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from loguru import logger


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для обмеження частоти запитів"""
    
    def __init__(self, rate_limit: float = 1.0):
        """
        Args:
            rate_limit: Мінімальний інтервал між повідомленнями в секундах
        """
        self.rate_limit = rate_limit
        self.user_timestamps: Dict[int, float] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Застосовуємо throttling тільки для повідомлень
        if not isinstance(event, Message):
            return await handler(event, data)
        
        user_id = event.from_user.id
        current_time = time.time()
        
        # Перевіряємо час останнього повідомлення користувача
        if user_id in self.user_timestamps:
            time_diff = current_time - self.user_timestamps[user_id]
            
            if time_diff < self.rate_limit:
                # Користувач надсилає повідомлення занадто часто
                logger.warning(
                    f"Throttling користувача {user_id}: "
                    f"інтервал {time_diff:.2f}s < {self.rate_limit}s"
                )
                
                # Можна відправити попередження (але не завжди, щоб не спамити)
                if time_diff < self.rate_limit / 2:
                    try:
                        await event.answer(
                            "⏳ Будь ласка, зачекайте трохи перед наступним запитом."
                        )
                    except Exception:
                        pass  # Ігноруємо помилки при відправці попередження
                
                return  # Не обробляємо повідомлення
        
        # Оновлюємо час останнього повідомлення
        self.user_timestamps[user_id] = current_time
        
        # Очищуємо старі записи (старше 1 години)
        if len(self.user_timestamps) > 1000:  # Оптимізація пам'яті
            cutoff_time = current_time - 3600  # 1 година
            self.user_timestamps = {
                uid: timestamp 
                for uid, timestamp in self.user_timestamps.items()
                if timestamp > cutoff_time
            }
        
        # Викликаємо handler
        return await handler(event, data)