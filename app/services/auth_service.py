import logging
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.passwords import get_password_hash, verify_password


from datetime import datetime, timedelta
from jose import JWTError, jwt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_user(username: str, password: str, db: Session):
    hashed_password = get_password_hash(password)
    db_user = User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def login_user(user: UserCreate, password: str, db: Session):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user and verify_password(password, db_user.hashed_password):
        return {"message": "Login successful"}
    return {"message": "Invalid credentials"}
