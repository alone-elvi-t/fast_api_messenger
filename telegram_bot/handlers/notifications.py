from aiogram import Router, types
from aiogram.filters import Command
import logging

# Создаем router для обработчиков уведомлений
notification_router = Router()

logger = logging.getLogger(__name__)

async def notify_command(message: types.Message):
    """Обработчик команды /notify для отправки уведомлений"""
    await message.reply("Это уведомление для вас!")

# Регистрируем обработчик команды notify через новый способ фильтрации
notification_router.message.register(notify_command, Command(commands=['notify']))
