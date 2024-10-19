from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Подключение к базе данных
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db/chat_db"

# Создание объекта engine для подключения к базе данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Фабрика сессий для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Получение сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
