from aiogram import Router, types
from aiogram.filters import Command
import logging

router = Router()
logger = logging.getLogger(__name__)

async def start_command(message: types.Message):
    """Обработчик команды /start"""
    await message.reply(
        "Привет! Я бот для уведомлений чата.\n"
        "Используйте /bind your_username для привязки вашего аккаунта."
    )

async def help_command(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
    Доступные команды:
    /start - Начать работу с ботом
    /bind username - Привязать ваш аккаунт чата
    /unbind - Отвязать аккаунт
    /status - Проверить статус привязки
    """
    await message.reply(help_text)

def register_base_handlers(dp):
    """Регистрация базовых обработчиков через Router"""
    dp.include_router(router)
    router.message.register(start_command, Command(commands=['start']))
    router.message.register(help_command, Command(commands=['help']))
