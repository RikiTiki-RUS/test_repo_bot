import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.engine import init_db
from bot.middlewares.db_session import DatabaseMiddleware
from handlers import groups

# Настройка логирования
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/bot.log", # Логи в файл
    filemode="a"
)
# Также дублируем в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(config.LOG_LEVEL)
logging.getLogger().addHandler(console_handler)

logger = logging.getLogger(__name__)

async def main():
    logger.info("Запуск бота...")
    
    # Инициализация БД
    await init_db()
    logger.info("База данных инициализирована.")

    # Создание бота и диспетчера
    bot = Bot(
        token=config.BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Подключаем мидлварь БД (глобально для всех хендлеров)
    dp.update.middleware(DatabaseMiddleware())

    # Регистрируем роутеры
    #dp.include_router(private.router)
    dp.include_router(groups.router)

    # Запуск polling (удаление обновлений при старте, чтобы не обрабатывать старый мусор)
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Polling запущен.")
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем.")
    finally:
        await bot.session.close()
        logger.info("Сессия бота закрыта.")

if __name__ == "__main__":
    # Создаем папку для логов, если нет
    import os
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    asyncio.run(main())