from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .student import Student
    from .subject import Subject
    from .semester import Semester


class Score(SQLModel, table=True):
    __tablename__ = "scores"

    score_id: int = Field(default=None, primary_key=True)
    student_id: Optional[int] = Field(default=None, foreign_key="students.student_id")
    subject_id: Optional[str] = Field(default=None, foreign_key="subjects.subject_id")
    semester_id: Optional[int] = Field(default=None, foreign_key="semesters.semester_id")
    score_4: Optional[float] = Field(default=None)
    comment_id: Optional[int] = Field(default=None)
    is_pass: bool = Field(default=False)
    score_10: Optional[float] = Field(default=None)

    # Relationships
    student: Optional["Student"] = Relationship(back_populates="scores")
    subject: Optional["Subject"] = Relationship(back_populates="scores")
    semester: Optional["Semester"] = Relationship(back_populates="scores")
