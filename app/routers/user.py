from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, APIRouter, Form
from app.models.user import User
from app.database import get_db
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM
from app.utils.passwords import get_password_hash

router = APIRouter()


# Получение текущего пользователя через токен
async def get_current_user(db: AsyncSession = Depends(get_db), token: str = ""):
    """
    Получает текущего пользователя на основе JWT токена.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Асинхронный запрос для поиска пользователя
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

# Маршрут для изменения профиля
@router.put("/profile", summary="Изменение профиля", tags=["User"])
async def update_profile(
    username: str = Form(..., description="Новое имя пользователя"),
    password: str = Form(None, description="Новый пароль"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Маршрут для изменения профиля пользователя.

    Позволяет пользователю изменить своё имя и пароль.
    """
    # Обновление имени пользователя
    current_user.username = username

    # Обновление пароля, если он был передан
    if password:
        current_user.hashed_password = get_password_hash(password)

    db.commit()
    return {"message": "Profile updated successfully"}


from fastapi import Query


@router.get(
    "/users/", summary="Получить список пользователей с пагинацией", tags=["User"]
)
async def get_users(
    skip: int = Query(0, description="Пропустить N записей"),
    limit: int = Query(10, description="Количество записей на странице"),
    db: AsyncSession = Depends(get_db),
):
    """
    Возвращает список пользователей с поддержкой пагинации.
    - `skip`: количество пропущенных записей (по умолчанию 0).
    - `limit`: количество записей, возвращаемых на одной странице (по умолчанию 10).
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users
