# Import models
from app.models.user_model import User
from app.models.role_model import Role
from app.models.major_model import Major
from app.models.intake_model import Intake
from app.models.class_model import Class
from app.models.student_model import Student
from app.models.course_model import Course
from app.models.score_model import Score
from app.models.notification_model import Notification
from app.models.upload_history_model import UploadHistory

__all__ = [
    "User",
    "Role",
    "Major",
    "Intake",
    "Class",
    "Student",
    "Course",
    "Score",
    "Notification",
    "UploadHistory",
]
