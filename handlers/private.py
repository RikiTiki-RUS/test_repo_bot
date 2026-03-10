from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Message
from aiogram.enums import ChatType

from database.models import User

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    """Обработчик команды /start."""
    # Получаем или создаем пользователя в БД
    user = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user_obj = user.scalar_one_or_none()

    if not user_obj:
        user_obj = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        session.add(user_obj)
        await session.commit()
    
    await message.answer(
        f"Привет, {message.from_user.first_name}! \n"
        "Я бот для сохранения сообщений из групп.\n"
        "Добавь меня в группу, и я буду пересылать сообщения тебе в ЛС."
    )

@router.message(F.chat.type.in_([ChatType.PRIVATE, ChatType.PRIVATE]))
async def echo_private(message: Message, session: AsyncSession):
    """Эхо в личные сообщения (для проверки)."""
    # Сохраняем сообщение в БД
    # Сначала убедимся, что пользователь есть
    user = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user_obj = user.scalar_one_or_none()
    
    if not user_obj:
        user_obj = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        session.add(user_obj)
        await session.commit()
        # Обновляем объект для получения ID
        await session.refresh(user_obj)

    msg_record = Message(
        user_id=user_obj.id,
        text=message.text,
        chat_id=message.chat.id
    )
    session.add(msg_record)
    # Коммит произойдет в мидлвари автоматически
    
    await message.answer(f"Эхо: {message.text}")
    