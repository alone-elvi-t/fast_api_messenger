from fastapi import FastAPI
from app.routes import auth, chat, main
from app.database import engine
from app.models import Base  # Импортируем Base из app/models/__init__.py
from app.models.user import User
from app.models.message import Message
from app.database import engine
from app.utils import templates

app = FastAPI(
    title="App for chatbot messenger",
    description="API для обмена мгновенными сообщениями между пользователями.",
    version="1.0.0",
)

# Подключаем маршруты
app.include_router(main.router, prefix="", tags=["Main"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# Создаём таблицу users
User.metadata.create_all(bind=engine)
# Создаём таблицу messages
Message.metadata.create_all(bind=engine)
