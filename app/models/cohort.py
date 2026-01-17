from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .class_model import Class
    from .training_program import TrainingProgram


class Cohort(SQLModel, table=True):
    __tablename__ = "cohorts"

    cohort_id: int = Field(default=None, primary_key=True)
    year_start: int = Field(unique=True)

    # Relationships
    classes: list["Class"] = Relationship(back_populates="cohort")
    training_programs: list["TrainingProgram"] = Relationship(back_populates="cohort")
