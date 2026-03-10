from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import async_session_maker

class DatabaseMiddleware(BaseMiddleware):
    """
    Мидлварь для внедрения сессии SQLAlchemy в данные события (event_data).
    Позволяет обращаться к session внутри хендлеров как к аргументу.
    """
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        async with async_session_maker() as session:
            data["session"] = session
            return await handler(event, data)