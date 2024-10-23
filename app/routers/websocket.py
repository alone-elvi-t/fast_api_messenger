"""Модуль для обработки WebSocket соединений."""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from app.models.user import User
from app.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Словарь для хранения активных WebSocket-соединений
active_connections = {}

@router.websocket("/ws/{username}")
async def websocket_endpoint(
    websocket: WebSocket, 
    username: str, 
    db: AsyncSession = Depends(get_db)
):
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
    logger.debug("[START] handle_message для %s", username)
    logger.debug("Сообщение: %s", message)

    if message.startswith('/'):
        await handle_command(websocket, username, message, db)
        return

    try:
        if ':' not in message:
            logger.error("Неверный формат сообщения")
            await websocket.send_text("Ошибка: используйте формат 'получатель:сообщение'")
            return

        recipient, content = message.split(':', 1)
        recipient = recipient.strip()
        content = content.strip()

        new_message = Message(
            content=content,
            sender=username,
            receiver=recipient,
            status='sent'  # Используем строку вместо enum
        )

        db.add(new_message)
        await db.commit()
        
        # Отправляем подтверждение отправителю
        await websocket.send_text(f"Вы -> {recipient}: {content}")

        # Отправляем сообщение получателю
        if recipient in active_connections:
            await active_connections[recipient].send_text(f"{username}: {content}")
            logger.debug("Сообщение отправлено получателю %s", recipient)

    except Exception as e:
        logger.error("Общая ошибка: %s", str(e))
        await websocket.send_text(f"Системная ошибка: {str(e)}")

async def handle_command(websocket: WebSocket, username: str, command: str, db: AsyncSession):
    logger.info(f"Обработка команды от {username}: {command}")
    if command.startswith("/get_history"):
        try:
            parts = command.split()
            if len(parts) != 2:
                await websocket.send_json({
                    "type": "error",
                    "message": "Неерный формат комады. Используйте: /get_history имя_пользователя"
                })
                return
                
            target_username = parts[1]
            history = await get_message_history(db, username, target_username)
            logger.info(f"Получена история для {username} и {target_username}: {history}")
            
            await websocket.send_json({
                "type": "history",
                "messages": history
            })
                
        except Exception as e:
            logger.error(f"Ошибка при получении истории: {str(e)}")
            await websocket.send_json({
                "type": "error",
                "message": f"Ошибка при получении истории: {str(e)}"
            })
    else:
        logger.warning(f"Неизвестная команда: {command}")
        await websocket.send_json({
            "type": "error",
            "message": "Неизвестная команда"
        })

async def get_message_history(db: AsyncSession, user1: str, user2: str):
    logger.info(f"Запрос истории сообщений между {user1} и {user2}")
    
    try:
        # Получаем сообщения из базы данных
        messages_query = select(Message).where(
            or_(
                and_(Message.sender == user1, Message.receiver == user2),
                and_(Message.sender == user2, Message.receiver == user1)
            )
        ).order_by(Message.timestamp)
        
        result = await db.execute(messages_query)
        messages = result.scalars().all()
        
        # Форматируем сообщения
        formatted_messages = []
        for msg in messages:
            formatted_message = f"{msg.sender}: {msg.content}"
            formatted_messages.append(formatted_message)
            
        logger.info(f"Найдено {len(formatted_messages)} сообщений")
        return formatted_messages
        
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {e}")
        return []





