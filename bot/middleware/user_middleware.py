from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger

from database.models.base import get_async_session
from database.repositories.user_repository import UserRepository


class UserMiddleware(BaseMiddleware):
    """Middleware для роботи з користувачами"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Отримуємо користувача з події
        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        
        if not user:
            return await handler(event, data)
        
        try:
            # Отримуємо сесію бази даних
            async for session in get_async_session():
                user_repo = UserRepository(session)
                
                # Отримуємо або створюємо користувача в базі даних
                db_user = await user_repo.get_by_telegram_id(user.id)
                
                if not db_user:
                    # Створюємо нового користувача
                    db_user = await user_repo.create_or_update_user(
                        telegram_id=user.id,
                        username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        language_code=user.language_code or "uk"
                    )
                    logger.info(f"Створено нового користувача: {user.id} (@{user.username})")
                else:
                    # Оновлюємо час останньої активності
                    await user_repo.update_last_seen(user.id)
                
                # Перевіряємо чи не заблокований користувач
                if db_user.is_banned:
                    logger.warning(f"Заблокований користувач спробував використати бота: {user.id}")
                    
                    # Відправляємо повідомлення про блокування
                    if isinstance(event, Message):
                        await event.answer(
                            f"❌ Ваш акаунт заблокований.\n"
                            f"Причина: {db_user.ban_reason or 'Не вказана'}\n\n"
                            f"Зверніться до адміністратора для розблокування."
                        )
                    elif isinstance(event, CallbackQuery):
                        await event.answer(
                            "❌ Ваш акаунт заблокований",
                            show_alert=True
                        )
                    
                    return  # Не викликаємо handler для заблокованих користувачів
                
                # Додаємо користувача до контексту
                data['db_user'] = db_user
                data['user_repo'] = user_repo
                data['db_session'] = session
                
                # Викликаємо handler
                result = await handler(event, data)
                break
                
        except Exception as e:
            logger.error(f"Помилка в UserMiddleware: {e}")
            # Якщо сталася помилка, все одно викликаємо handler
            result = await handler(event, data)
        
        return result