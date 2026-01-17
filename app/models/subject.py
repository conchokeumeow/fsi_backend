from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .score import Score
    from .program_subject import ProgramSubject
    from .criteria_subject import CriteriaSubject


class Subject(SQLModel, table=True):
    __tablename__ = "subjects"

    subject_id: str = Field(unique=True, index=True, primary_key=True)
    name: str = Field(index=True)
    credits: int

    # Relationships
    scores: list["Score"] = Relationship(back_populates="subject")
    program_subjects: list["ProgramSubject"] = Relationship(back_populates="subject")
    criteria_subjects: list["CriteriaSubject"] = Relationship(back_populates="subject")
