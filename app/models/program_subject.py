from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .training_program import TrainingProgram
    from .subject import Subject


class ProgramSubject(SQLModel, table=True):
    __tablename__ = "program_subjects"

    program_subject_id: Optional[int] = Field(default=None, primary_key=True)
    training_program_id: Optional[int] = Field(default=None, foreign_key="training_programs.training_program_id")
    subject_id: Optional[str] = Field(default=None, foreign_key="subjects.subject_id")
    is_required: bool

    # Relationships
    training_program: Optional["TrainingProgram"] = Relationship(back_populates="program_subjects")
    subject: Optional["Subject"] = Relationship(back_populates="program_subjects")
