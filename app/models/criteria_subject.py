from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .graduation_criteria import GraduationCriteria
    from .subject import Subject


class CriteriaSubject(SQLModel, table=True):
    __tablename__ = "criteria_subjects"

    criteria_subject_id: Optional[int] = Field(default=None, primary_key=True)
    graduation_criteria_id: Optional[int] = Field(default=None, foreign_key="graduation_criteria.graduation_criteria_id")
    subject_id: Optional[str] = Field(default=None, foreign_key="subjects.subject_id")
    credits: int

    # Relationships
    graduation_criteria: Optional["GraduationCriteria"] = Relationship(back_populates="criteria_subjects")
    subject: Optional["Subject"] = Relationship(back_populates="criteria_subjects")
