from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User

from app.database import get_db

from app.utils.jwt import verify_token


def get_current_user(token: str, db: Session = Depends(get_db)):
    username = verify_token(token)

    user = db.query(User).filter(User.username == username).first()

    if user in None:
        raise HTTPException(status_code=401, default="User not found")
    return user


def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denided")
    return current_user