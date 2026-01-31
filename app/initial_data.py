"""
Script to initialize the database with initial data (Superuser, Roles)
Run this script once to setup the system.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path to ensure imports work
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.config import settings
from app.core.db import engine
from app.core.security import get_password_hash
from app.models.role_model import Role
from app.models.user_model import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init_db(session: Session) -> None:
    # 1. Create Superuser Role
    superuser_role = session.exec(
        select(Role).where(Role.role_name == "Superuser")
    ).first()

    if not superuser_role:
        superuser_role = Role(
            role_name="Superuser",
            is_superuser=True
        )
        session.add(superuser_role)
        session.commit()
        session.refresh(superuser_role)
        logger.info(f"Role 'Superuser' created with ID {superuser_role.role_id}")
    else:
        logger.info("Role 'Superuser' already exists")

    # 2. Create Default Roles (Teacher, Student) if missing
    default_roles = ["Teacher", "Student", "Academic Affairs"]
    for r_name in default_roles:
        role = session.exec(select(Role).where(Role.role_name == r_name)).first()
        if not role:
            session.add(Role(role_name=r_name, is_superuser=False))
            logger.info(f"Role '{r_name}' created")
    
    session.commit()

    # 3. Create Superuser
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()

    if not user:
        user = User(
            email=settings.FIRST_SUPERUSER,
            fullname=settings.FIRST_SUPERUSER_NAME,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            role_id=superuser_role.role_id,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info(f"Superuser created: {settings.FIRST_SUPERUSER}")
    else:
        logger.info(f"Superuser already exists: {settings.FIRST_SUPERUSER}")


def main() -> None:
    logger.info("Creating initial data")
    with Session(engine) as session:
        init_db(session)
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
