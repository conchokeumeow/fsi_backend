from typing import TYPE_CHECKING, Optional, List
from datetime import date
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.class_model import Class
    from app.models.score_model import Score

class Student(SQLModel, table=True):
    __tablename__ = "student"
    
    student_id: str = Field(primary_key=True, max_length=50)
    fullname: str = Field(max_length=255)
    dob: Optional[date] = Field(default=None)
    gpa: Optional[float] = Field(default=None)
    class_id: Optional[int] = Field(default=None, foreign_key="class.class_id")
    
    # Relationships
    class_: Optional["Class"] = Relationship(back_populates="students")
    scores: List["Score"] = Relationship(back_populates="student")
