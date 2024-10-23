"""Модуль, содержащий схемы пользователя для приложения."""

from fastapi import Form
from pydantic import BaseModel


class UserCreate:
    """Класс для создания нового пользователя из данных формы."""

    def __init__(self, username: str = Form(...), password: str = Form(...)):
        """
        Инициализирует объект UserCreate.

        Args:
            username (str): Имя пользователя.
            password (str): Пароль пользователя.
        """
        self.username = username
        self.password = password


class UserResponse(BaseModel):
    """Схема для отображения данных пользователя в ответе."""

    id: int
    username: str

    class Config:
        """Конфигурация для модели Pydantic."""
        from_attribute = True
