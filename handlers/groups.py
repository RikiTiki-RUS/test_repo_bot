import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, ChatMemberUpdated
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Message

from database.models import User, Message

logger = logging.getLogger(__name__)
router = Router()

# Фильтр: только группы и супергруппы
@router.message(F.text)
async def capture_group_message(message: Message, session: AsyncSession, bot: Bot):
    """
    Ловит сообщения в группах, сохраняет в БД и пытается отправить в ЛС автору.
    """
    logger.info("Хэндлер поймал сообщение")
    if not message.from_user or not message.text:
        # Игнорируем сообщения от имени группы или без текста (фото и т.д. для MVP)
        return

    user_telegram_id = message.from_user.id
    logger.info("Добавили айди пользователя")
    
    # 1. Находим или создаем пользователя в БД
    user = await session.execute(
        select(User).where(User.telegram_id == user_telegram_id)
    )
    user_obj = user.scalar_one_or_none()
    logger.info("Присвоили и нашли пользователя")

    if not user_obj:
        logger.info("Пользователя нет: добавляем")
        user_obj = User(
            telegram_id=user_telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        session.add(user_obj)
        await session.commit()
        logger.info("Сохранили пользователя в БД")
        await session.refresh(user_obj)
        logger.info("Обновили сессию подключения к БД")
    logger.info("Переходим к сохранению сообщения в БД")
    # 2. Сохраняем сообщение в БД
    msg_record = Message(
        user_id=user_obj.id,
        text=message.text,
        chat_id=message.chat.id
    )
    logger.info("Данные получены")
    session.add(msg_record)
    logger.info("Данные записаны")
    await session.commit()
    logger.info("Данные доавлены в БД")
    # Коммит будет в мидлвари

    # 3. Пытаемся отправить копию в ЛС
    try:
        await bot.send_message(
            chat_id=user_telegram_id,
            text=f"📢 Сообщение из группы (ID: {message.chat.id}):\n\n{message.text}"
        )
    except TelegramForbiddenError:
        # Пользователь заблокировал бота или никогда не запускал его в ЛС
        logger.warning(
            f"Не удалось отправить сообщение пользователю {user_telegram_id}. "
            "Возможно, бот заблокирован."
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в ЛС: {e}")