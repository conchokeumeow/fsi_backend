import sys
import os

# ======================
# FIX PYTHONPATH
# ======================
# env.py nằm ở backend/app/alembic/env.py
# → cần add thư mục "backend" vào sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, BASE_DIR)

# Debug để chắc chắn
print(">>> PYTHONPATH:", sys.path)

# Load env variables explicitly
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.core.config import settings  # noqa

# Models import - import all models here for Alembic to detect
from app.models.user_model import User  # noqa
from app.models.role_model import Role  # noqa
from app.models.class_model import Class  # noqa
from app.models.student_model import Student  # noqa
from app.models.major_model import Major  # noqa
from app.models.intake_model import Intake  # noqa
from app.models.course_model import Course  # noqa
from app.models.score_model import Score  # noqa
from app.models.notification_model import Notification  # noqa
from app.models.upload_history_model import UploadHistory  # noqa

target_metadata = SQLModel.metadata


def get_url() -> str:
    return str(settings.SQLALCHEMY_DATABASE_URI)


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
