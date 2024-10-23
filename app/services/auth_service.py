"""Модуль, предоставляющий сервисы аутентификации."""

import logging
from datetime import datetime

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.passwords import get_password_hash, verify_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_user(username: str, password: str, db: Session) -> User:
    """
    Регистрирует нового пользователя в системе.

    Args:
        username (str): Имя пользователя.
        password (str): Пароль пользователя.
        db (Session): Сессия базы данных.

    Returns:
        User: Объект зарегистрированного пользователя.
    """
    hashed_password = get_password_hash(password)
    db_user = User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def login_user(username: str, password: str, db: Session) -> dict:
    """
    Аутентифицирует пользователя.

    Args:
        username (str): Имя пользователя.
        password (str): Пароль пользователя.
        db (Session): Сессия базы данных.

    Returns:
        dict: Словарь с сообщением о результате аутентификации.
    """
    db_user = db.query(User).filter(User.username == username).first()
    if db_user and verify_password(password, db_user.hashed_password):
        return {"message": "Вход выполнен успешно"}
    return {"message": "Неверные учетные данные"}
