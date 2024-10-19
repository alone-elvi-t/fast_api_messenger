from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def register_user(username: str, password: str, db: Session):
    hashed_password = get_password_hash(password)
    db_user = User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return (
        db_user  # Возвращаем объект пользователя, который преобразуется в UserResponse
    )


def login_user(user: UserCreate, db: Session):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user and verify_password(user.password, db_user.hashed_password):
        return {"message": "Login successful"}
    return {"message": "Invalid credentials"}
