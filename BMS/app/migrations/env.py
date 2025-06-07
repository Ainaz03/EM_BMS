import os, sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# чтобы Python видел app/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.core.config import settings
from app.core.database import Base   # или from app/db/base import Base
import app.models                  # регистрируем все модели

# Настраиваем Config и метаданные
config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # создаём движок вручную из безопасного URL
    connectable = create_engine(
        settings.DATABASE_URL,
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