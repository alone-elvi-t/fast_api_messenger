import logging
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.utils.passwords import verify_password
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Функция для проверки пользователя
async def authenticate_user(db: AsyncSession, username: str, password: str):
    """
    Аутентификация пользователя.

    Выполняет поиск пользователя в базе данных по имени пользователя и проверяет, соответствует ли введенный пароль сохраненному хешу пароля.

    Аргументы:
        db (AsyncSession): Асинхронная сессия для работы с базой данных.
        username (str): Имя пользователя.
        password (str): Пароль пользователя.

    Возвращает:
        User: Объект пользователя, если аутентификация прошла успешно.

    Возвращает None, если аутентификация не удалась.
    """
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        logging.error(f"Пользователь с именем {username} не найден.")
        return None

    # Проверка пароля
    if not verify_password(password, user.hashed_password):
        logging.error(f"Неверный пароль для пользователя {username}.")
        return None

    logging.info(f"Пользователь {username} успешно аутентифицирован.")
    return user



async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Получаем текущего пользователя на основе токена из cookies.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    # Асинхронное выполнение запроса для поиска пользователя
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user
