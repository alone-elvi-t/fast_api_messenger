"""Модуль, содержащий схемы Pydantic для сообщений."""

from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    """
    Схема для создания нового сообщения.
    
    Атрибуты:
        receiver_id (int): Идентификатор получателя сообщения.
        content (str): Содержание сообщения.
    """
    receiver_id: int
    content: str


class MessageResponse(BaseModel):
    """
    Схема ответа для сообщения.
    
    Атрибуты:
        id (int): Уникальный идентификатор сообщения.
        sender_id (int): Идентификатор отправителя сообщения.
        receiver_id (int): Идентификатор получателя сообщения.
        content (str): Содержание сообщения.
        timestamp (datetime): Время отправки сообщения.
    """
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime

    class Config:
        """
        Конфигурация для модели Pydantic.
        
        Атрибуты:
            from_attributes (bool): Разрешает создание модели из атрибутов объекта ORM.
        """
        from_attributes = True
