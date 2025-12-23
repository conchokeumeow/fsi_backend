"""
Students Upload Route
Upload CSV file để import danh sách sinh viên
"""
from typing import Any

from fastapi import APIRouter, UploadFile, File, Depends
from sqlmodel import Session

from app.api.deps import CurrentUser, SessionDep
from app.api.services.student_service import StudentService
from app.models.upload_history_model import UploadHistory

router = APIRouter()


@router.post(
    "/upload-csv",
    summary="Upload CSV file to import students",
    response_model=UploadHistory
)
async def upload_students_csv(
    current_user: CurrentUser,
    session: SessionDep,
    file: UploadFile = File(...),
) -> Any:
    """
    Upload CSV file chứa thông tin sinh viên.
    
    **CSV Format:**
    - Required columns: `student_id`, `fullname`
    - Optional columns: `dob`, `gpa`, `class_id`
    
    **Date format:**
    - Supported: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY
    
    **Example CSV:**
    ```
    student_id,fullname,dob,gpa,class_id
    SV001,Nguyen Van A,2000-01-15,3.5,1
    SV002,Tran Thi B,2000-05-20,3.8,1
    ```
    
    **Process:**
    1. Create upload history record (status: PROCESSING)
    2. Validate CSV format and headers
    3. Process each row:
       - If student exists: update information
       - If student doesn't exist: create new
    4. Update history with result (status: COMPLETED/FAILED)
    
    **Response:**
    Returns UploadHistory với thông tin:
    - total_processed: Tổng số rows đã xử lý
    - success_count: Số rows thành công
    - failure_count: Số rows thất bại
    - status: COMPLETED hoặc FAILED
    """
    service = StudentService(session)
    result = await service.import_students_from_csv(file, current_user)
    
    return result
