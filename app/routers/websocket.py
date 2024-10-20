import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Словарь для хранения активных WebSocket-соединений
active_connections = {}


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logging.info(f"ROUTER::WEBSOCKET::websocket_endpoint")

    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Сообщение получено: {data}")


@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    """
    Основной WebSocket маршрут для подключения пользователей.
    Каждое подключение сохраняется в словаре active_connections с ключом username.
    Также реализована отправка сообщений между пользователями и уведомления о подключении/отключении.
    """
    await websocket.accept()
    logging.info(f"ROUTER::WEBSOCKET::websocket_endpoint {username}")
    active_connections[username] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Проверяем, содержит ли сообщение разделитель ":"
            if ":" in data:
                recipient, message = data.split(":", 1)  # Разделяем сообщение на получателя и текст
            else:
                # Если формат неправильный, отправляем уведомление отправителю
                await websocket.send_text("Сообщение должно быть в формате 'recipient:message'.")
                continue
            
            # Если получатель подключён, отправляем ему сообщение
            if recipient in active_connections:
                await active_connections[recipient].send_text(f"Сообщение от {username}: {message}")
            else:
                # Если получателя нет, отправляем уведомление отправителю
                await websocket.send_text(f"Пользователь {recipient} не подключён.")
    except WebSocketDisconnect:
        # Удаляем соединение при отключении
        del active_connections[username]
        await websocket.close()