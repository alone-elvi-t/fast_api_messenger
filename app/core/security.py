from datetime import timedelta

# Секретный ключ для шифрования токенов
SECRET_KEY = "g$Rl9Z0CAUSiHmJBQ1@hmK!fLJwZ!cs4"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 10


def get_token_expire_time():
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
