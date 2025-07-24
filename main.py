import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

# Додаємо поточну директорію до sys.path
sys.path.append(str(Path(__file__).parent))

from config.settings.base import settings
from database.models.base import init_db
from bot.handlers import routers
from bot.middleware.user_middleware import UserMiddleware
from bot.middleware.throttling_middleware import ThrottlingMiddleware


async def setup_logging():
    """Налаштування логування"""
    # Видаляємо стандартний логер loguru
    logger.remove()
    
    # Додаємо логування в файл
    logger.add(
        settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    # Додаємо логування в консоль
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}:{function}:{line}</cyan> | {message}"
    )
    
    # Налаштовуємо стандартний Python logging для aiogram
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


async def setup_bot_commands(bot: Bot):
    """Налаштування команд бота"""
    from aiogram.types import BotCommand
    
    commands = [
        BotCommand(command="start", description="🚀 Запустити бота"),
        BotCommand(command="help", description="ℹ️ Допомога"),
        BotCommand(command="menu", description="🏠 Головне меню"),
        BotCommand(command="downloads", description="📋 Мої завантаження"),
        BotCommand(command="settings", description="⚙️ Налаштування"),
        BotCommand(command="stats", description="📊 Статистика"),
    ]
    
    await bot.set_my_commands(commands)
    logger.info("Команди бота налаштовано")


async def on_startup(bot: Bot):
    """Дії при запуску бота"""
    logger.info("Запуск бота...")
    
    # Ініціалізація бази даних
    try:
        await init_db()
        logger.info("База даних ініціалізована")
    except Exception as e:
        logger.error(f"Помилка ініціалізації бази даних: {e}")
        raise
    
    # Налаштування команд бота
    try:
        await setup_bot_commands(bot)
    except Exception as e:
        logger.error(f"Помилка налаштування команд: {e}")
    
    # Отримання інформації про бота
    try:
        bot_info = await bot.get_me()
        logger.info(f"Бот запущено: @{bot_info.username} ({bot_info.full_name})")
    except Exception as e:
        logger.error(f"Помилка отримання інформації про бота: {e}")


async def on_shutdown(bot: Bot):
    """Дії при зупинці бота"""
    logger.info("Зупинка бота...")
    
    # Тут можна додати очищення ресурсів
    # Наприклад, закриття з'єднань з базою даних
    
    logger.info("Бот зупинено")


async def main():
    """Головна функція"""
    # Налаштування логування
    await setup_logging()
    
    logger.info("Початок запуску YouTube Bot")
    
    try:
        # Створення бота
        bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML
            )
        )
        
        # Створення диспетчера з FSM storage
        dp = Dispatcher(storage=MemoryStorage())
        
        # Додавання middleware
        dp.message.middleware(UserMiddleware())
        dp.callback_query.middleware(UserMiddleware())
        dp.message.middleware(ThrottlingMiddleware())
        
        # Реєстрація роутерів
        for router in routers:
            dp.include_router(router)
        
        logger.info(f"Зареєстровано {len(routers)} роутерів")
        
        # Реєстрація startup та shutdown хендлерів
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Запуск polling
        logger.info("Запуск polling...")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Критична помилка: {e}")
        raise
    finally:
        logger.info("Завершення роботи програми")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Отримано сигнал переривання. Зупинка бота...")
    except Exception as e:
        logger.error(f"Неочікувана помилка: {e}")
        sys.exit(1)