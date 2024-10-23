"""Модуль для настройки и управления подключением к базе данных."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:password@db:5432/chat_db"

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание фабрики сессий
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Зависимость для получения сессии
async def get_db():
    """Асинхронный генератор для получения сессии базы данных."""
    async with AsyncSessionLocal() as session:
        yield session

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронный генератор для получения сессии базы данных."""
    async with AsyncSessionLocal() as session:
        yield session

# Убедитесь, что эта функция определена и не закомментирована
