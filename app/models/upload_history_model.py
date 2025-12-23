from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.user_model import User

class UploadHistory(SQLModel, table=True):
    __tablename__ = "upload_history"

    id: int = Field(primary_key=True)
    file_name: str
    status: str = Field(default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    success_count: int = Field(default=0)
    failure_count: int = Field(default=0)
    total_processed: int = Field(default=0)
    error_message: Optional[str] = Field(default=None)  # Error message if failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by_id: Optional[int] = Field(default=None, foreign_key="users.user_id")
    
    # Relationship
    created_by: Optional["User"] = Relationship(back_populates="upload_histories")
