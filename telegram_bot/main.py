import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from telegram_bot.config import settings
from telegram_bot.handlers.base import register_base_handlers
from telegram_bot.handlers.notifications import notification_router
from telegram_bot.utils.logger import setup_logger

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        
        # Регистрация обработчиков
        register_base_handlers(self.dp)
        self.dp.include_router(notification_router)
    
    async def start(self):
        """Запуск бота"""
        setup_logger()
        logger.info("Starting Telegram bot...")
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error occurred: {e}")

if __name__ == "__main__":
    import asyncio
    bot_instance = TelegramBot()
    asyncio.run(bot_instance.start())
