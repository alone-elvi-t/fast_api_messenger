from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routes import auth, chat

app = FastAPI()

# Подключение папки для статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")

# Подключение маршрутов
app.include_router(auth.router)
app.include_router(chat.router)
