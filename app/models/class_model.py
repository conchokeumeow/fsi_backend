from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .cohort import Cohort
    from .major import Major
    from .student import Student


class Class(SQLModel, table=True):
    __tablename__ = "classes"

    class_id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    cohort_id: Optional[int] = Field(default=None, foreign_key="cohorts.cohort_id")
    major_id: Optional[int] = Field(default=None, foreign_key="majors.major_id")

    # Relationships
    cohort: Optional["Cohort"] = Relationship(back_populates="classes")
    major: Optional["Major"] = Relationship(back_populates="classes")
    students: list["Student"] = Relationship(back_populates="class_")
