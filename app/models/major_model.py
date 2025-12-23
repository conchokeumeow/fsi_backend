from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.class_model import Class
    from app.models.course_model import Course

class Major(SQLModel, table=True):
    __tablename__ = "major"
    
    major_id: int = Field(primary_key=True)
    major_name: str = Field(max_length=255)
    
    # Relationships
    classes: List["Class"] = Relationship(back_populates="major")
    courses: List["Course"] = Relationship(back_populates="major")
