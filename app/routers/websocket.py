"""Модуль для обработки WebSocket соединений."""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from app.models.user import User
from app.database import get_async_session
from app.telegram_bot.services.notification_service import NotificationService

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Словарь для хранения активных WebSocket-соединений
active_connections = {}

notification_service = NotificationService()

@router.websocket("/ws/{username}")
async def websocket_endpoint(
    websocket: WebSocket, 
    username: str, 
    db: AsyncSession = Depends(get_async_session)
):
    """
    Обрабатывает WebSocket соединение для конкретного пользователя.

    Args:
        websocket (WebSocket): Объект WebSocket соединения.
        username (str): Имя пользователя.
        db (AsyncSession): Асинхронная сессия базы данных.
    """
    await websocket.accept()
    active_connections[username] = websocket
    logger.debug("WebSocket подключен для пользователя %s", username)
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug("Получено сообщение от %s: %s", username, data)
            await handle_message(websocket, username, data, db)
                
    except WebSocketDisconnect:
        if username in active_connections:
            del active_connections[username]

async def handle_message(websocket: WebSocket, username: str, message: str, db: AsyncSession):
    """
    Обрабатывает входящее сообщение от пользователя.

    Args:
        websocket (WebSocket): Объект WebSocket соединения.
        username (str): Имя отправителя.
        message (str): Содержание сообщения.
        db (AsyncSession): Асинхронная сессия базы данных.
    """
    logger.debug("[START] handle_message для %s", username)
    logger.debug("Сообщение: %s", message)

    if message.strip().startswith('/'):
        logger.debug("Обнаружена команда: %s", message)
        await handle_command(websocket, username, message.strip(), db)
        return

    if ':' not in message:
        logger.error("Неверный формат сообщения")
        await websocket.send_text("Ошибка: используйте формат 'получатель:сообщение'")
        return

    receiver, content = message.split(':', 1)
    receiver = receiver.strip()
    content = content.strip()

    new_message = Message(
        content=content,
        sender_id=username,
        recipient_id=receiver,
    )

    db.add(new_message)
    await db.commit()
    
    await websocket.send_text(f"Вы -> {receiver}: {content}")

    if receiver in active_connections:
        await active_connections[receiver].send_text(f"{username}: {content}")
        logger.debug("Сообщение отправлено получателю %s", receiver)

    is_online = await check_user_online(db, receiver)
    
    if not is_online:
        await notification_service.send_notification(
            username=receiver,
            sender=username,
            message=content
        )
        
async def handle_command(websocket: WebSocket, username: str, command: str, db: AsyncSession):
    """
    Обрабатывает команды, отправленные пользователем.

    Args:
        websocket (WebSocket): Объект WebSocket соединения.
        username (str): Имя пользователя, отправившего команду.
        command (str): Текст команды.
        db (AsyncSession): Асинхронная сессия базы данных.
    """
    logger.debug("Обработка команды: %s", command)
    
    if command.startswith("/get_history"):
        try:
            parts = command.split()
            logger.debug("Части команды: %s", parts)
            
            if len(parts) != 2:
                await websocket.send_json({
                    "type": "error",
                    "message": "Неверный формат команды. Используйте: /get_history имя_пользователя"
                })
                return
                
            target_username = parts[1]
            logger.debug("Запрос истории для пользователя: %s", target_username)
            
            history = await get_message_history(db, username, target_username)
            logger.debug("Получена история: %s", history)
            
            await websocket.send_json({
                "type": "history",
                "messages": history
            })
                
        except Exception as e:
            logger.error("Ошибка при обработке команды get_history: %s", str(e))
            await websocket.send_json({
                "type": "error",
                "message": f"Ошибка при получении истории: {str(e)}"
            })
    else:
        logger.warning("Неизвестная команда: %s", command)
        await websocket.send_json({
            "type": "error",
            "message": "Неизвестная команда"
        })

async def get_message_history(db: AsyncSession, user1: str, user2: str):
    """
    Получает историю сообщений между двумя пользователями.

    Args:
        db (AsyncSession): Асинхронная сессия базы данных.
        user1 (str): Имя первого пользователя.
        user2 (str): Имя второго пользователя.

    Returns:
        list: Список сообщений в формате словарей.
    """
    logger.info(f"Запрос истории сообщений между {user1} и {user2}")
    
    try:
        messages_query = select(Message).where(
            or_(
                and_(Message.sender_id == user1, Message.recipient_id == user2),
                and_(Message.sender_id == user2, Message.recipient_id == user1)
            )
        ).order_by(Message.created_at)
        
        result = await db.execute(messages_query)
        messages = result.scalars().all()
        
        formatted_messages = [
            {
                "sender": msg.sender_id,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]
            
        logger.info(f"Найдено {len(formatted_messages)} сообщений")
        return formatted_messages
        
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {e}")
        return []

async def check_user_online(db: AsyncSession, username: str) -> bool:
    """
    Проверяет, находится ли пользователь в сети.

    Args:
        db (AsyncSession): Асинхронная сессия базы данных.
        username (str): Имя пользователя для проверки.

    Returns:
        bool: True, если пользователь в сети, иначе False.
    """
    query = select(User.is_online).where(User.username == username)
    result = await db.execute(query)
    is_online = result.scalar_one_or_none()
    return is_online if is_online is not None else False
