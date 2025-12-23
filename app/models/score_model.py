from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.student_model import Student
    from app.models.course_model import Course

class Score(SQLModel, table=True):
    __tablename__ = "score"
    
    id_score: int = Field(primary_key=True)
    student_id: Optional[str] = Field(default=None, foreign_key="student.student_id")
    course_id: Optional[int] = Field(default=None, foreign_key="course.course_id")
    score: Optional[float] = Field(default=None)
    
    # Relationships
    student: Optional["Student"] = Relationship(back_populates="scores")
    course: Optional["Course"] = Relationship(back_populates="scores")
