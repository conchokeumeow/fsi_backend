from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .major import Major
    from .cohort import Cohort
    from .program_subject import ProgramSubject
    from .program_certificate import ProgramCertificate


class TrainingProgram(SQLModel, table=True):
    __tablename__ = "training_programs"

    training_program_id: int = Field(default=None, primary_key=True)
    major_id: Optional[int] = Field(default=None, foreign_key="majors.major_id")
    cohort_id: Optional[int] = Field(default=None, foreign_key="cohorts.cohort_id")
    name: str = Field(index=True)
    credits: Optional[str] = Field(default=None)

    # Relationships
    major: Optional["Major"] = Relationship(back_populates="training_programs")
    cohort: Optional["Cohort"] = Relationship(back_populates="training_programs")
    program_subjects: list["ProgramSubject"] = Relationship(back_populates="training_program")
    program_certificates: list["ProgramCertificate"] = Relationship(back_populates="training_program")
