from pydantic_settings import BaseSettings
from typing import Optional

class BotConfig(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    LOG_LEVEL: str = Field(default="INFO")
    
    class Config:
        env_file = ".env"

config = BotConfig()
