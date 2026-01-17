from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    role_id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    is_superuser: bool = Field(default=False)

    # Relationships
    users: list["User"] = Relationship(back_populates="role")
