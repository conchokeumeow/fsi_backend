from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .credential import Credential
    from .program_certificate import ProgramCertificate
    from .criteria_certificate import CriteriaCertificate


class Certificate(SQLModel, table=True):
    __tablename__ = "certificates"

    certificate_id: int = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    name: str = Field(index=True)
    note: str

    # Relationships
    credentials: list["Credential"] = Relationship(back_populates="certificate")
    program_certificates: list["ProgramCertificate"] = Relationship(back_populates="certificate")
    criteria_certificates: list["CriteriaCertificate"] = Relationship(back_populates="certificate")
