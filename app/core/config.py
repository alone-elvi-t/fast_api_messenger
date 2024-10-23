"""
Модуль конфигурации приложения.

Этот модуль содержит класс Settings, который использует pydantic_settings
для управления настройками приложения, загружаемыми из переменных окружения.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Класс настроек приложения.

    Атрибуты:
        DATABASE_URL (str): URL для подключения к базе данных.
        SECRET_KEY (str): Секретный ключ для шифрования и безопасности.
        TELEGRAM_BOT_TOKEN (str): Токен для Telegram бота.
    """

    DATABASE_URL: str
    SECRET_KEY: str
    TELEGRAM_BOT_TOKEN: str

    class Config:
        """
        Конфигурация для класса Settings.

        Атрибуты:
            env_file (str): Путь к файлу с переменными окружения.
        """

        env_file = ".env"


settings = Settings()
