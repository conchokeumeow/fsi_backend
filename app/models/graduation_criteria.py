from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .major import Major
    from .criteria_subject import CriteriaSubject
    from .criteria_certificate import CriteriaCertificate


class GraduationCriteria(SQLModel, table=True):
    __tablename__ = "graduation_criteria"

    graduation_criteria_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    major_id: Optional[int] = Field(default=None, foreign_key="majors.major_id")
    credits: int
    default_id: Optional[int] = Field(default=None)

    # Relationships
    major: Optional["Major"] = Relationship(back_populates="graduation_criterias")
    criteria_subjects: list["CriteriaSubject"] = Relationship(back_populates="graduation_criteria")
    criteria_certificates: list["CriteriaCertificate"] = Relationship(back_populates="graduation_criteria")
