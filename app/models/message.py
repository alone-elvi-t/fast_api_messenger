from app.models import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class MessageStatus(enum.Enum):
    sent = "sent"
    delivered = "delivered"
    read = "read"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    # Отправитель и получатель сообщения
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Содержание сообщения
    content = Column(String, nullable=False)

    # Метка времени
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Статус сообщения (по умолчанию - отправлено)
    status = Column(Enum(MessageStatus), default=MessageStatus.sent, nullable=False)

    # Связи с моделью User (если требуется)
    sender = relationship(
        "User", foreign_keys=[sender_id], lazy="select", backref="sent_messages"
    )
    receiver = relationship(
        "User", foreign_keys=[receiver_id], lazy="select", backref="received_messages"
    )

    # Индексы для оптимизации запросов
    __table_args__ = (
        Index(
            "ix_sender_receiver", "sender_id", "receiver_id"
        ),  # Индекс на пары sender/receiver
    )
