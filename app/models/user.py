from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .role import Role


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    email: Optional[str] = Field(default=None, unique=True)
    role_id: Optional[int] = Field(default=None, foreign_key="roles.role_id")
    is_active: bool = Field(default=True)
    avatar_url: Optional[str] = Field(default=None)

    # Relationships
    role: Optional["Role"] = Relationship(back_populates="users")
