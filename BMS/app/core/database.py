from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 1) Движок для подключения к БД
engine = create_async_engine(settings.DATABASE_URL_asyncpg, echo=True)

# 2) Фабрика для создания сессий
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 3) Базовый класс для всех моделей
Base = declarative_base()

# 4) Функция-зависимость для FastAPI, чтобы получать сессию в эндпоинтах
async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
