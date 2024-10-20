from fastapi import Form
from pydantic import BaseModel


class UserCreate:
    # Извлечение данных из формы
    def __init__(self, username: str = Form(...), password: str = Form(...)):
        self.username = username
        self.password = password


# Схема для отображения данных пользователя в ответе
class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
