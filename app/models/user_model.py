from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.role_model import Role
    from app.models.class_model import Class
    from app.models.upload_history_model import UploadHistory
    from app.models.notification_model import Notification

class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: int = Field(primary_key=True)
    fullname: Optional[str] = Field(default=None, max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    is_active: bool = Field(default=True)
    role_id: Optional[int] = Field(default=None, foreign_key="roles.role_id")
    
    # Relationships
    role: Optional["Role"] = Relationship(back_populates="users")
    classes: List["Class"] = Relationship(back_populates="user")
    upload_histories: List["UploadHistory"] = Relationship(back_populates="created_by")
    notifications: List["Notification"] = Relationship(back_populates="user")
