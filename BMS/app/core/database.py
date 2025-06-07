from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# Движок для подключения к БД
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Фабрика для создания сессий
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для всех моделей
Base = declarative_base()


async def get_async_session() -> AsyncSession:
    """
    Зависимость (dependency) для получения асинхронной сессии БД.
    Обеспечивает открытие и закрытие сессии для каждого запроса.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()