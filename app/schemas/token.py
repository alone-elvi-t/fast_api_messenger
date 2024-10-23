"""Модуль, содержащий схемы для работы с токенами аутентификации."""

from pydantic import BaseModel


# Схема для создания токена
class Token(BaseModel):
    """Схема, представляющая токен аутентификации."""
    access_token: str
    token_type: str


# Схема для передачи токена
class TokenData(BaseModel):
    username: str | None = None

