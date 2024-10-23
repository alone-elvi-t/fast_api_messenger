from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    DATABASE_URL: str = Field(default="postgresql://user:password@localhost:5437/chat_db")
    LOG_LEVEL: str = Field(default="INFO")

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
