from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .student import Student
    from .certificate import Certificate


class Credential(SQLModel, table=True):
    __tablename__ = "credentials"

    credential_id: int = Field(default=None, primary_key=True)
    student_id: Optional[int] = Field(default=None, foreign_key="students.student_id")
    certificate_id: Optional[int] = Field(default=None, foreign_key="certificates.certificate_id")
    note: str

    # Relationships
    student: Optional["Student"] = Relationship(back_populates="credentials")
    certificate: Optional["Certificate"] = Relationship(back_populates="credentials")
