"""
Модуль для обработки аутентификации и авторизации пользователей.

Этот модуль содержит маршруты и функции для регистрации пользователей,
входа в систему, получения информации о текущем пользователе и других
операций, связанных с аутентификацией.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.utils.auth import authenticate_user, get_current_user
from app.utils.jwt import create_access_token, verify_token
from app.utils.passwords import get_password_hash
from app.utils.utils import templates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.get("/me")
async def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Возвращает информацию о текущем пользователе.
    """
    return current_user


@router.get("/register/", response_class=HTMLResponse)
async def register_form(request: Request):
    """
    Возвращает HTML-страницу с формой регистрации.

    Args:
        request (Request): Объект запроса FastAPI.

    Returns:
        TemplateResponse: HTML-страница с формой регистрации.
    """
    logger.info("Попытка перенаправления с html-страницы в post запрос %s", request)
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register/", summary="Регистрация пользователя")
async def register(
    user_data: RegisterRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Регистрация нового пользователя.

    Args:
        user_data (RegisterRequest): Данные нового пользователя.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        dict: Сообщение об успешной регистрации.

    Raises:
        HTTPException: Если пользователь с таким именем уже существует.
    """
    username = user_data.username
    password = user_data.password

    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "User successfully registered"}


@router.get("/login/", response_class=HTMLResponse)
async def login_form(request: Request):
    """
    Возвращает HTML-страницу с формой входа.

    Args:
        request (Request): Объект запроса FastAPI.

    Returns:
        TemplateResponse: HTML-страница с формой входа.
    """
    logger.info("Попытка входа через страницу браузера")
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login/", summary="Вход пользователя")
async def login_user(
    credentials: LoginRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Маршрут для входа пользователя.

    Args:
        credentials (LoginRequest): Модель с данными для входа (имя пользователя и пароль).
        db (AsyncSession): Асинхронная сессия для работы с базой данных.

    Returns:
        RedirectResponse: Перенаправление на страницу чата при успешной аутентификации.

    Raises:
        HTTPException: Возвращает статус 400, если аутентификация не удалась.
    """
    user = await authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})

    redirect_response = RedirectResponse(url="/chat/chat/", status_code=302)
    redirect_response.set_cookie(key="access_token", value=access_token, httponly=True)

    return redirect_response


@router.get("/users/me")
async def read_authenticated_user(token: str = Depends(verify_token)):
    """
    Защищенный маршрут для получения информации о текущем пользователе.
    """
    logger.info("Токен пользователя: %s", token)
    return {"message": f"Authenticated as {token}"}
