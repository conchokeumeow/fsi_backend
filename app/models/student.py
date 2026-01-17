from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from .class_model import Class
    from .major import Major
    from .score import Score
    from .credential import Credential


class Student(SQLModel, table=True):
    __tablename__ = "students"

    student_id: int = Field(default=None, primary_key=True)
    full_name: str = Field(index=True)
    dob: Optional[date] = Field(default=None)
    class_id: Optional[int] = Field(default=None, foreign_key="classes.class_id")
    major_id: Optional[int] = Field(default=None, foreign_key="majors.major_id")
    status: Optional[str] = Field(default=None)

    # Relationships
    class_: Optional["Class"] = Relationship(back_populates="students")
    major: Optional["Major"] = Relationship(back_populates="students")
    scores: list["Score"] = Relationship(back_populates="student")
    credentials: list["Credential"] = Relationship(back_populates="student")
