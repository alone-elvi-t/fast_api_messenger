"""Модуль, определяющий модель сообщения и связанные с ней структуры."""

import enum
from datetime import datetime
from sqlalchemy.sql import expression

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, text
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy import event, types


from app.models import Base




class Message(Base):
    """Модель сообщения."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    sender = Column(String, ForeignKey("users.username"), nullable=False)
    receiver = Column(String, ForeignKey("users.username"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(
        String(20),
        nullable=False,
        server_default=text("'sent'")
    )

    __table_args__ = (
        Index("ix_sender_receiver", "sender", "receiver"),
    )

    def to_dict(self):
        """Преобразует объект сообщения в словарь."""
        return {
            "id": self.id,
            "content": self.content,
            "sender": self.sender,
            "receiver": self.receiver,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }

    def __repr__(self):
        return f"Message(id={self.id}, sender={self.sender}, receiver={self.receiver}, status={self.status})"

    def __str__(self):
        return f"Message(sender={self.sender}, receiver={self.receiver}, content={self.content})"

@event.listens_for(Message, 'before_insert')
def lowercase_status(mapper, connection, target):
    if target.status:
        target.status = target.status.lower()

@event.listens_for(Message, 'before_update')
def lowercase_status_on_update(mapper, connection, target):
    if target.status:
        target.status = target.status.lower()
