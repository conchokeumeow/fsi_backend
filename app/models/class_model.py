from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.major_model import Major
    from app.models.intake_model import Intake
    from app.models.student_model import Student

class Class(SQLModel, table=True):
    __tablename__ = "class"
    
    class_id: int = Field(primary_key=True)
    class_name: str = Field(max_length=255, unique=True)
    major_id: Optional[int] = Field(default=None, foreign_key="major.major_id")
    user_id: Optional[int] = Field(default=None, foreign_key="users.user_id")  # Teacher
    intake_id: Optional[int] = Field(default=None, foreign_key="intake.intake_id")
    
    # Relationships
    major: Optional["Major"] = Relationship(back_populates="classes")
    user: Optional["User"] = Relationship(back_populates="classes")  # Teacher
    intake: Optional["Intake"] = Relationship(back_populates="classes")
    students: List["Student"] = Relationship(back_populates="class_")

