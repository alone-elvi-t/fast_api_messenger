"""Модуль для выполнения запросов к базе данных."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import engine 
from app.models.chat import Chat
from app.models.message import Message
from app.models.user import User

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_user_history_from_db(username: str):
    """Получает историю сообщений пользователя из базы данных."""
    async with AsyncSessionLocal() as session:
        query = select(Message).filter(Message.username == username).order_by(Message.timestamp)
        result = await session.execute(query)
        return result.scalars().all()

async def is_admin(session: AsyncSession, user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором."""
    query = select(User.is_admin).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none() or False

async def get_user_chats(session: AsyncSession, user_id: int, is_owner: bool = False) -> list[int]:
    """Получает список чатов пользователя."""
    query = select(Chat.id).join(Chat.users).where(User.id == user_id)
