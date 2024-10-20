from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.utils.jwt import verify_token
from app.database import get_db
from app.models.user import User
from app.utils.passwords import get_password_hash

router = APIRouter()


# Получение текущего пользователя через токен
def get_current_user(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    username = verify_token(token)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# Маршрут для изменения профиля
@router.put("/profile", summary="Изменение профиля", tags=["User"])
async def update_profile(
    username: str = Form(..., description="Новое имя пользователя"),
    password: str = Form(None, description="Новый пароль"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
):
    """
    Возвращает список пользователей с поддержкой пагинации.
    - `skip`: количество пропущенных записей (по умолчанию 0).
    - `limit`: количество записей, возвращаемых на одной странице (по умолчанию 10).
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users
