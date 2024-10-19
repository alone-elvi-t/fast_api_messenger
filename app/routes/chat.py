from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.orm import Session
from app.schemas.message import MessageCreate, MessageResponse
from app.database import get_db
from datetime import datetime

router = APIRouter()


@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Сообщение получено: {data}")


@router.post(
    "/send_message/", response_model=MessageResponse, summary="Отправка сообщения"
)
async def send_message(message: MessageCreate, db: Session = Depends(get_db)):
    """
    Отправка сообщения от пользователя другому пользователю.
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
