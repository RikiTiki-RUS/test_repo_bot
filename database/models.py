from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    """Модель пользователя Telegram."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Связь с сообщениями (один ко многим)
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")

class Message(Base):
    """Модель сохраненного сообщения."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="messages")