from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.major_model import Major
    from app.models.intake_model import Intake
    from app.models.score_model import Score

class Course(SQLModel, table=True):
    __tablename__ = "course"
    
    course_id: int = Field(primary_key=True)
    course_name: str = Field(max_length=255)
    tcdh: Optional[str] = Field(default=None, max_length=50)  # Tín chỉ đại học
    is_bb: Optional[bool] = Field(default=False)  # Bắt buộc
    major_id: Optional[int] = Field(default=None, foreign_key="major.major_id")
    intake_id: Optional[int] = Field(default=None, foreign_key="intake.intake_id")
    
    # Relationships
    major: Optional["Major"] = Relationship(back_populates="courses")
    intake: Optional["Intake"] = Relationship(back_populates="courses")
    scores: List["Score"] = Relationship(back_populates="course")
