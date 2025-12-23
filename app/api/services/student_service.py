"""
CSV Upload Service
Xử lý logic upload và parse CSV file cho students
"""
import csv
from datetime import datetime
from io import StringIO
from typing import Dict, Any, List, Tuple

from fastapi import UploadFile, HTTPException
from sqlmodel import Session, select

from app.models.student_model import Student
from app.models.upload_history_model import UploadHistory
from app.models.user_model import User


class StudentService:
    """Service to handle all student related operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def import_students_from_csv(
        self, 
        file: UploadFile, 
        current_user: User
    ) -> UploadHistory:
        """
        Upload và process CSV file chứa thông tin sinh viên
        
        Args:
            file: CSV file upload
            current_user: User đang thực hiện upload
            
        Returns:
            UploadHistory: Record chứa kết quả upload
            
        Raises:
            HTTPException: Nếu file không hợp lệ
        """
        # Validate file
        self._validate_file(file)
        
        # Create upload history record
        upload_history = self._create_upload_history(file.filename, current_user.user_id)
        
        try:
            # Parse CSV content
            rows = await self._parse_csv(file)
            
            # Process rows
            result = self._process_students(rows, current_user)
            
            # Update history with success
            self._update_history_success(upload_history, result)
            
        except Exception as e:
            # Update history with failure
            self._update_history_failure(upload_history, str(e))
            raise
        
        finally:
            self.session.commit()
            self.session.refresh(upload_history)
        
        return upload_history
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate file type"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="File name is required")
        
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400, 
                detail="Only CSV files are allowed. Please upload a .csv file"
            )
    
    def _create_upload_history(
        self, 
        filename: str, 
        user_id: int
    ) -> UploadHistory:
        """Create upload history record"""
        upload_history = UploadHistory(
            file_name=filename,
            created_by_id=user_id,
            status="PROCESSING"
        )
        self.session.add(upload_history)
        self.session.commit()
        self.session.refresh(upload_history)
        return upload_history
    
    async def _parse_csv(self, file: UploadFile) -> List[Dict[str, str]]:
        """
        Parse CSV file content
        
        Returns:
            List of dicts, mỗi dict là 1 row
        """
        # Read file content
        content = await file.read()
        
        # Decode (support UTF-8 with BOM)
        try:
            decoded_content = content.decode('utf-8-sig')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="File encoding error. Please use UTF-8 encoding"
            )
        
        # Parse CSV
        csv_file = StringIO(decoded_content)
        csv_reader = csv.DictReader(csv_file)
        
        # Normalize headers (lowercase, strip whitespace)
        if csv_reader.fieldnames:
            csv_reader.fieldnames = [
                name.strip().lower() 
                for name in csv_reader.fieldnames
            ]
        
        # Validate required fields
        self._validate_csv_headers(csv_reader.fieldnames)
        
        # Convert to list
        return list(csv_reader)
    
    def _validate_csv_headers(self, fieldnames: List[str] | None) -> None:
        """Validate CSV has required headers"""
        if not fieldnames:
            raise HTTPException(
                status_code=400,
                detail="CSV file is empty or has no headers"
            )
        
        required_fields = ["student_id", "fullname"]
        missing_fields = [
            field for field in required_fields 
            if field not in fieldnames
        ]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_fields)}. "
                       f"Required: student_id, fullname. "
                       f"Optional: dob, gpa, class_id"
            )
    
    def _process_students(
        self, 
        rows: List[Dict[str, str]], 
        current_user: User
    ) -> Dict[str, int]:
        """
        Process CSV rows và create/update students
        
        Returns:
            Dict với keys: total_processed, success_count, failure_count
        """
        total_processed = 0
        success_count = 0
        failure_count = 0
        
        for row in rows:
            total_processed += 1
            try:
                self._process_single_student(row, current_user)
                self.session.flush()
                success_count += 1
                
            except Exception as row_error:
                print(f"Error processing row {total_processed}: {row_error}")
                failure_count += 1
        
        return {
            "total_processed": total_processed,
            "success_count": success_count,
            "failure_count": failure_count
        }
    
    def _process_single_student(
        self, 
        row: Dict[str, str], 
        current_user: User
    ) -> None:
        """Process a single CSV row"""
        # Extract and validate data
        student_id = row.get("student_id", "").strip()
        fullname = row.get("fullname", "").strip()
        
        if not student_id or not fullname:
            raise ValueError("Missing required fields: student_id or fullname")
        
        # Parse optional fields
        dob = self._parse_date(row.get("dob", "").strip())
        gpa = self._parse_float(row.get("gpa", "").strip())
        class_id = self._parse_int(row.get("class_id", "").strip())
        
        # Check if student exists
        existing_student = self.session.exec(
            select(Student).where(Student.student_id == student_id)
        ).first()
        
        if existing_student:
            # Update existing student
            existing_student.fullname = fullname
            existing_student.dob = dob
            existing_student.gpa = gpa
            existing_student.class_id = class_id
            self.session.add(existing_student)
        else:
            # Create new student
            new_student = Student(
                student_id=student_id,
                fullname=fullname,
                dob=dob,
                gpa=gpa,
                class_id=class_id,
                owner_id=current_user.user_id
            )
            self.session.add(new_student)
    
    @staticmethod
    def _parse_date(date_str: str):
        """Parse date string to date object"""
        if not date_str:
            return None
        
        # Try common date formats
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def _parse_float(value_str: str) -> float | None:
        """Parse string to float"""
        if not value_str:
            return None
        try:
            return float(value_str)
        except ValueError:
            return None
    
    @staticmethod
    def _parse_int(value_str: str) -> int | None:
        """Parse string to int"""
        if not value_str:
            return None
        try:
            return int(value_str)
        except ValueError:
            return None
    
    def _update_history_success(
        self, 
        history: UploadHistory, 
        result: Dict[str, int]
    ) -> None:
        """Update history with success result"""
        history.status = "COMPLETED"
        history.total_processed = result["total_processed"]
        history.success_count = result["success_count"]
        history.failure_count = result["failure_count"]
        self.session.add(history)
    
    def _update_history_failure(
        self, 
        history: UploadHistory, 
        error_message: str
    ) -> None:
        """Update history with failure"""
        history.status = "FAILED"
        history.error_message = error_message
        self.session.add(history)
