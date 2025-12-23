from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.class_model import Class
    from app.models.course_model import Course

class Intake(SQLModel, table=True):
    __tablename__ = "intake"
    
    intake_id: int = Field(primary_key=True)
    kdb: Optional[str] = Field(default=None, max_length=50)  # Khóa đào tạo
    tdc: Optional[str] = Field(default=None, max_length=50)  # Thời điểm chính
    sum_tc: Optional[int] = Field(default=None)  # Tổng tín chỉ
    
    # Relationships
    classes: List["Class"] = Relationship(back_populates="intake")
    courses: List["Course"] = Relationship(back_populates="intake")
