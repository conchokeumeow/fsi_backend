from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .student import Student
    from .class_model import Class
    from .training_program import TrainingProgram
    from .graduation_criteria import GraduationCriteria


class Major(SQLModel, table=True):
    __tablename__ = "majors"

    major_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    # Relationships
    students: list["Student"] = Relationship(back_populates="major")
    classes: list["Class"] = Relationship(back_populates="major")
    training_programs: list["TrainingProgram"] = Relationship(back_populates="major")
    graduation_criterias: list["GraduationCriteria"] = Relationship(back_populates="major")
