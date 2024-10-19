import logging
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import get_password_hash, register_user, login_user
from app.database import get_db
from app.utils import templates
from app.models.user import User

from fastapi.responses import HTMLResponse

router = APIRouter()


# Маршрут для отображения страницы регистрации (GET-запрос)
@router.get("/register/", response_class=HTMLResponse)
async def register_form(request: Request):
    """
    Возвращает HTML-страницу с формой регистрации.
    """
    return templates.TemplateResponse("register.html", {"request": request})


# Маршрут для обработки регистрации (POST-запрос)
@router.post("/register/", response_model=UserResponse)
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    body = await request.form()
    logging.info(f"Request body: {body}")  # Логируем тело запроса

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    new_user = register_user(username, password, db)
    return new_user

@router.post("/login/", summary="Вход пользователя")
async def login(user: UserResponse, db: Session = Depends(get_db)):
    """
    Вход пользователя в систему.
    - **username**: имя пользователя
    - **password**: пароль для пользователя
    """
    return login_user(user, db)


@router.get("/login/", response_class=HTMLResponse)
async def login(request: Request):
    """
    Возвращает HTML-страницу с формой входа
    """
    return templates.TemplateResponse("login.html", {"request": request})
