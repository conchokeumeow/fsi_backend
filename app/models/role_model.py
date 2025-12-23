from typing import TYPE_CHECKING, List
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user_model import User

class Role(SQLModel, table=True):
    __tablename__ = "roles"
    
    role_id: int = Field(primary_key=True)
    role_name: str = Field(max_length=100, unique=True)
    is_superuser: bool = Field(default=False)
    
    # Relationship
    users: List["User"] = Relationship(back_populates="role")
