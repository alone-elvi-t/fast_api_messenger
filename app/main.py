"""Основной модуль приложения, содержащий конфигурацию FastAPI и маршрутизацию."""

from contextlib import asynccontextmanager

# import asyncio  # Удалите эту строку, если asyncio не используется напрямую
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from app.routers import auth, chat, main, user, websocket
from app.database import engine
from app.models import Base  # Импортируем Base из app/models/__init__.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управляет жизненным циклом приложения."""
    await async_create_tables()
    yield

app = FastAPI(
    title="App for chatbot messenger",
    description="API для обмена мгновенными сообщениями между пользователями.",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Создаем основной роутер
main_router = APIRouter()

# Группируем маршруты
main_router.include_router(main.router, tags=["Main"])
main_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
main_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
main_router.include_router(user.router, prefix="/user", tags=["User"])
main_router.include_router(websocket.router, prefix="/websocket", tags=["Websocket"])

# Подключаем основной роутер к приложению
app.include_router(main_router)

# Асинхронная функция для создания всех таблиц
async def async_create_tables():
    """Асинхронно создает все таблицы в базе данных."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
