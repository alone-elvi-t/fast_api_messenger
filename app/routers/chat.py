"""Модуль, содержащий маршруты для функциональности чата."""

from typing import List
from datetime import datetime

import logging
from fastapi import APIRouter, WebSocket, Depends, Request
from fastapi.responses import HTMLResponse
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.message import MessageCreate, MessageResponse
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.message import Message

from app.utils.utils import templates
from app.database import get_async_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/chat", response_class=HTMLResponse)
async def get_chat_page(
    request: Request, current_user: User = Depends(get_current_user)
):
    """
    Рендеринг страницы чата с текущим пользователем.
    """

    return templates.TemplateResponse(
        "chat.html", {"request": request, "current_user": current_user}
    )

@router.get("/history/{username}", response_model=List[MessageResponse])
async def get_chat_history(username: str, db: AsyncSession = Depends(get_async_session)):
    """
    Получает историю сообщений для указанного пользователя.
    
    Args:
        username (str): Имя пользователя, для которого запрашивается история.
        db (AsyncSession): Асинхронная сессия базы данных.
    
    Returns:
        List[MessageResponse]: Список сообщений пользователя.
    """
    query = select(Message).filter(
        (Message.sender == username) | (Message.recipient == username)
    ).order_by(Message.timestamp)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return [MessageResponse.from_orm(message) for message in messages]

@router.get("/users/list")
async def get_users_list(db: AsyncSession = Depends(get_async_session)):
    """
    Получает список всех пользователей.
    
    Args:
        db (AsyncSession): Асинхронная сессия базы данных.
    
    Returns:
        List[str]: Список имен пользователей.
    """
    query = select(User.username)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users

@router.post(
    "/send_message/", response_model=MessageResponse, summary="Отправка сообщения"
)
async def send_message(message: MessageCreate):
    """
    Отправка сообщения от пользоватля другому пользователю.
    - **receiver_id**: ID получателя
    - **content**: Текст сообщения
    - **timestamp**: Текущая дата.
    """
    # Пример сохранения сообщения (логика должна быть реализована)
    new_message = MessageResponse(
        id=1,
        sender_id=1,
        receiver_id=message.receiver_id,
        content=message.content,
        timestamp=datetime.now(),
    )
    return new_message




