from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .training_program import TrainingProgram
    from .certificate import Certificate


class ProgramCertificate(SQLModel, table=True):
    __tablename__ = "program_certificates"

    program_certificate_id: Optional[int] = Field(default=None, primary_key=True)
    training_program_id: Optional[int] = Field(default=None, foreign_key="training_programs.training_program_id")
    certificate_id: Optional[int] = Field(default=None, foreign_key="certificates.certificate_id")
    note: Optional[str] = Field(default=None)

    # Relationships
    training_program: Optional["TrainingProgram"] = Relationship(back_populates="program_certificates")
    certificate: Optional["Certificate"] = Relationship(back_populates="program_certificates")
