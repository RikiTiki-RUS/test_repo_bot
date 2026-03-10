from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import config
from database.models import Base

# Создаем движок. 
# echo=True для отладки SQL запросов в консоль (в продакшене лучше False)
engine = create_async_engine(config.DB_URL, echo=False, future=True)

# Фабрика сессий
async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

async def init_db():
    """Создает таблицы в БД при запуске."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    """Генератор сессий для мидлвари."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()