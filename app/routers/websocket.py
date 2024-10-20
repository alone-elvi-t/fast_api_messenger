from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Словарь для хранения активных WebSocket-соединений
active_connections = {}


from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Словарь для хранения активных WebSocket-соединений
active_connections = {}


@router.websocket("/websocket/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    """
    Основной WebSocket маршрут для подключения пользователей.
    Каждое подключение сохраняется в словаре active_connections с ключом username.
    Также реализована отправка сообщений между пользователями и уведомления о подключении/отключении.
    """
    await websocket.accept()

    # Уведомляем всех подключённых пользователей о новом подключении
    for connection in active_connections.values():
        await connection.send_text(f"Пользователь {username} подключился.")

    active_connections[username] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            recipient, message = data.split(
                ":", 1
            )  # Формат сообщения: "recipient:message"

            # Отправляем сообщение получателю
            if recipient in active_connections:
                await active_connections[recipient].send_text(
                    f"Сообщение от {username}: {message}"
                )
            else:
                await websocket.send_text(f"Пользователь {recipient} не подключён.")
    except WebSocketDisconnect:
        del active_connections[username]

        # Уведомляем всех подключённых пользователей об отключении
        for connection in active_connections.values():
            await connection.send_text(f"Пользователь {username} отключился.")

        await websocket.close()
