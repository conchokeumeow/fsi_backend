from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .graduation_criteria import GraduationCriteria
    from .certificate import Certificate


class CriteriaCertificate(SQLModel, table=True):
    __tablename__ = "criteria_certificates"

    criteria_certificate_id: int = Field(default=None, primary_key=True)
    graduation_criteria_id: Optional[int] = Field(default=None, foreign_key="graduation_criteria.graduation_criteria_id")
    certificate_id: Optional[int] = Field(default=None, foreign_key="certificates.certificate_id")

    # Relationships
    graduation_criteria: Optional["GraduationCriteria"] = Relationship(back_populates="criteria_certificates")
    certificate: Optional["Certificate"] = Relationship(back_populates="criteria_certificates")
