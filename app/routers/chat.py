import logging
from fastapi import APIRouter, WebSocket, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.schemas.message import MessageCreate, MessageResponse
from app.database import get_db
from datetime import datetime
from app.utils.auth import get_current_user
from app.models.user import User

from app.utils.utils import templates

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
