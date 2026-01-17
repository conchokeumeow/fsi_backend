from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .score import Score


class Semester(SQLModel, table=True):
    __tablename__ = "semesters"

    semester_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    is_current: bool = Field(default=False)

    # Relationships
    scores: list["Score"] = Relationship(back_populates="semester")
