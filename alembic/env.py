from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from app.models import Base  # Импортируйте вашу базовую модель (Base) для использования автогенерации миграций
from app.database import DATABASE_URL  # Получите строку подключения из конфигурации вашего приложения

# Настройка логирования
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Подключение вашей базы данных
target_metadata = Base.metadata

# Синхронный URL для Alembic
# DATABASE_SYNC_URL = DATABASE_URL.replace('+asyncpg', '')
DATABASE_SYNC_URL = "postgresql://user:password@localhost:5437/chat_db"
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = DATABASE_SYNC_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = create_engine(
        DATABASE_SYNC_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
