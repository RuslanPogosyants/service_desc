import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database.models import Base
from app.core.config import Settings

settings = Settings()

# Это объект конфигурации Alembic, который предоставляет доступ к значениям в используемом .ini файле.
config = context.config

# Настройка логгеров, если указан файл конфигурации.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные для поддержки автогенерации миграций.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме."""
    # Получаем секцию конфигурации из alembic.ini
    config_section = config.get_section(
        config.config_ini_section, {}
    )  # Используем пустой словарь по умолчанию

    # Создаем подключение к базе данных
    connectable = engine_from_config(
        config_section,  # Передаем словарь конфигурации
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
