# Import all models for Alembic auto-detection and relationship resolution
from .role import Role
from .user import User
from .major import Major
from .cohort import Cohort
from .class_model import Class
from .semester import Semester
from .subject import Subject
from .student import Student
from .certificate import Certificate
from .score import Score
from .training_program import TrainingProgram
from .program_subject import ProgramSubject
from .program_certificate import ProgramCertificate
from .graduation_criteria import GraduationCriteria
from .criteria_subject import CriteriaSubject
from .criteria_certificate import CriteriaCertificate
from .credential import Credential

__all__ = [
    "Role",
    "User",
    "Major",
    "Cohort",
    "Class",
    "Semester",
    "Subject",
    "Student",
    "Certificate",
    "Score",
    "TrainingProgram",
    "ProgramSubject",
    "ProgramCertificate",
    "GraduationCriteria",
    "CriteriaSubject",
    "CriteriaCertificate",
    "Credential",
]
