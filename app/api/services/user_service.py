from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.user_model import User


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(
        User.email == email,
        User.is_active == True
        )
        return self.session.exec(statement).first()

    # def create_user(self, user_create: UserCreate) -> User:
    #     db_obj = User.model_validate(
    #         user_create,
    #         update={"hashed_password": get_password_hash(user_create.password)},
    #     )
    #     self.session.add(db_obj)
    #     self.session.commit()
    #     self.session.refresh(db_obj)
    #     return db_obj

    # def update_user(self, db_user: User, user_in: UserUpdate) -> Any:
    #     user_data = user_in.model_dump(exclude_unset=True)
    #     extra_data = {}
    #     if "password" in user_data:
    #         password = user_data["password"]
    #         hashed_password = get_password_hash(password)
    #         extra_data["hashed_password"] = hashed_password
    #     db_user.sqlmodel_update(user_data, update=extra_data)
    #     self.session.add(db_user)
    #     self.session.commit()
    #     self.session.refresh(db_user)
    #     return db_user

    def authenticate(self, email: str, password: str) -> User | None:
        db_user = self.get_user_by_email(email=email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user 