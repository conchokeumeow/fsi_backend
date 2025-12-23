from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.user_model import User

class Notification(SQLModel, table=True):
    __tablename__ = "notification"
    
    notification_id: int = Field(primary_key=True)
    fullname: Optional[str] = Field(default=None, max_length=255)
    dob: Optional[date] = Field(default=None)
    gpa: Optional[float] = Field(default=None)
    user_id: Optional[int] = Field(default=None, foreign_key="users.user_id")

    # Relationship
    user: Optional["User"] = Relationship(back_populates="notifications")
