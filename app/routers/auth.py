import logging
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse

from app.utils.auth import authenticate_user
from app.database import get_db
from app.utils.passwords import get_password_hash
from app.utils.utils import templates
from app.models.user import User
from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    verify_token,
)

from app.utils.roles import admin_required
from app.services.auth_service import register_user
from app.utils.auth import authenticate_user
from app.schemas.token import Token

from fastapi.security import OAuth2PasswordBearer

from fastapi.responses import HTMLResponse, RedirectResponse, Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Пример защищённого маршрута
@router.get("/users/me")
async def read_users_me(token: str = Depends(verify_token)):
    return {"message": f"Authenticated as {token}"}


# Маршрут для отображения страницы регистрации (GET-запрос)
@router.get("/register/", response_class=HTMLResponse)
async def register_form(request: Request):
    """
    Возвращает HTML-страницу с формой регистрации.
    """
    logging.info(f"Попытка перенаправления с html-страницы в post запрос {request}")
    return templates.TemplateResponse("register.html", {"request": request})


# Маршрут для обработки регистрации (POST-запрос)
@router.post("/register/", response_model=UserResponse)
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    body = await request.form()
    logging.info(f"Request body: {body}")  # Логируем тело запроса

    logger.info(f"Попытка регистрации пользователя с именем: {username}")

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        logger.warning(f"Имя пользователя уже занято: {username}")
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = register_user(username, password, db)
    logger.info(f"Пользователь зарегистрирован: {new_user.username}")
    return new_user


@router.get("/login/", response_class=HTMLResponse)
async def login(request: Request):
    """
    Возвращает HTML-страницу с формой входа
    """
    logger.info(f"Поаытка входа через страницу браузера")
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login/", summary="Вход пользователя")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    logging.info(f"ROUTER::AUTH::LOGIN::POST::response {response}")

    # Аутентификация
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Генерация токена
    access_token = create_access_token(data={"sub": user.username})

    # Сохранение токена в cookies
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response = RedirectResponse(url="/chat/chat/", status_code=302)
    logging.info(f"ROUTER::AUTH::LOGIN::POST::response {response}")
    return {"message": "Login successful"}
    # return response


# @router.post("/login/", summary="Вход пользователя")
# async def login(
#     username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
# ):
#     """
#     Аутентификация пользователя и генерация JWT токенов (access и refresh).

#     Перенаправляет пользователя на страницу чата после успешного входа.
#     """

#     logging.info(f"POST_LOGIN {username}")
#     user = authenticate_user(db, username, password)


#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid credentials")

#     logging.info(f"POST_LOGIN::if user {user.username}")

#     # Генерация токенов
#     access_token = create_access_token(data={"sub": user.username})
#     refresh_token = create_refresh_token(data={"sub": user.username})
#     response.set_cookie(key="access_token", value=access_token, httponly=True)

#     logging.info(f"POST_LOGIN::if access_token {access_token}")
#     logging.info(f"POST_LOGIN::if refresh_token {refresh_token}")


#     # Вы можете сохранить токены в cookies, если хотите использовать их для последующих запросов
#     response = RedirectResponse(url="/chat/chat/", status_code=302)
#     logging.info(f"ROUTERS:POST_LOGIN:: response {response}")
#     response.set_cookie(key="access_token", value=access_token, httponly=True)
#     response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)



#     return response


# Пример защищённого маршрута
@router.get("/users/me")
async def read_users_me(token: str = Depends(verify_token)):
    logger.info(f"{token}")
    return {"message": f"Authenticated as {token}"}


@router.post(
    "/token/refresh/",
    response_model=Token,
    summary="Обновление JWT токена",
    tags=["Authentication"],
)
async def refresh_token(token: str = Depends(oauth2_scheme)):
    """
    Обновление access токена с использованием refresh токена.

    Требуется:
    - `refresh_token`: токен для обновления access токена.

    Возвращает:
    - `access_token`: новый токен для доступа к защищённым ресурсам.
    """
    username = verify_token(token)
    access_token = create_access_token(data={"sub": username})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/password-reset/request/",
    summary="Запрос на сброс пароля",
    tags=["Password Reset"],
)
async def request_password_reset(
    username: str = Form(..., description="Имя пользователя для сброса пароля"),
    db: Session = Depends(get_db),
):
    """
    Генерация токена для сброса пароля и отправка пользователю (в реальном приложении отправляется по email).

    Возвращает токен для сброса пароля.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_password_reset_token(data={"sub": user.username})

    return {"reset_token": reset_token}


@router.post("/password-reset/", summary="Сброс пароля", tags=["Password Reset"])
async def reset_password(
    token: str = Form(..., description="Токен для сброса пароля"),
    new_password: str = Form(..., description="Новый пароль"),
    db: Session = Depends(get_db),
):
    """
    Сброс пароля пользователя с использованием токена для сброса пароля.

    Требует:
    - `token`: токен для сброса пароля, сгенерированный при запросе на сброс пароля.
    - `new_password`: новый пароль, который будет установлен для пользователя.

    Возвращает сообщение об успешном сбросе пароля.
    """
    username = verify_token(token)

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.commit()

    return {"message": "Password reset successful"}


@router.post(
    "/token/refresh/",
    response_model=Token,
    summary="Обновление JWT токена",
    tags=["Authentication"],
)
async def refresh_token(token: str = Depends(oauth2_scheme)):
    """
    Обновление access токена с использованием refresh токена.

    Требуется:
    - `refresh_token`: токен для обновления access токена.

    Возвращает:
    - `access_token`: новый токен для доступа к защищённым ресурсам.
    """
    username = verify_token(token)
    access_token = create_access_token(data={"sub": username})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/password-reset/", summary="Сброс пароля", tags=["Password Reset"])
async def reset_password(
    token: str = Form(..., description="Токен для сброса пароля"),
    new_password: str = Form(..., description="Новый пароль"),
    db: Session = Depends(get_db),
):
    """
    Сброс пароля пользователя с использованием токена для сброса пароля.

    Требует:
    - `token`: токен для сброса пароля, сгенерированный при запросе на сброс пароля.
    - `new_password`: новый пароль, который будет установлен для пользователя.

    Возвращает сообщение об успешном сбросе пароля.
    """
    username = verify_token(token)

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.commit()

    return {"message": "Password reset successful"}


@router.get("/admin/panel", summary="Панель администратора", tags=["Admin"])
async def admin_panel(current_user: User = Depends(admin_required)):
    """
    Доступно только администраторам.
    Возвращает панель администратора.
    """
    return {"message": "Welcome to the admin panel", "user": current_user.username}
