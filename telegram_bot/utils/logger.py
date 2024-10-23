import logging

def setup_logger():
    """Настройка логгера для приложения"""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
