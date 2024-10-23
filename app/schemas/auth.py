"""Схемы аутентификации для приложения."""

from pydantic import BaseModel

class LoginRequest(BaseModel):
    """Схема запроса для входа в систему."""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """Схема запроса для регистрации пользователя."""
    username: str
    password: str



