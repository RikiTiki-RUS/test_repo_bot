import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

class Config:
    """Класс конфигурации приложения."""
    
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DB_URL: str = os.getenv("DB_URL", "sqlite+aiosqlite:///./database.db")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN not found in environment variables!")
        return cls

config = Config.validate()