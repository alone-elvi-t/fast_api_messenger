from pydantic import BaseModel


# Схема для создания токена
class Token(BaseModel):
    access_token: str
    token_type: str


# Схема для передачи токена
class TokenData(BaseModel):
    username: str | None = None
