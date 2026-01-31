
from typing import Any
from fastapi import APIRouter, UploadFile, File, Depends
from app.api.deps import CurrentUser, SessionDep
from app.api.services.score_service import ScoreService
from app.models.upload_history_model import UploadHistory

router = APIRouter()

@router.post(
    "/upload-scores",
    summary="Upload Excel/CSV file to import scores",
    response_model=UploadHistory
)
async def upload_scores(
    current_user: CurrentUser,
    session: SessionDep,
    file: UploadFile = File(...)
) -> Any:
    """
    Upload file Excel hoặc CSV chứa bảng điểm sinh viên.
    
    **Định dạng hỗ trợ:**
    - .xlsx, .xls, .csv (Hỗ trợ tốt tiếng Việt Unicode)
    
    **Cấu trúc file:**
    - **Dòng (Rows)**: Mỗi dòng đại diện cho một sinh viên.
    - **Cột thông tin SV**: Hệ thống nhận diện các cột như 'Mã SV', 'Họ lót', 'Tên', 'Ngày sinh'...
    - **Cột điểm**: Tất cả các cột còn lại được coi là môn học.
    
    **Cơ chế khớp Môn học (Course Matching):**
    - Tên cột phải khớp với tên môn học hiển thị trong hệ thống.
    - Ví dụ: "Cơ sở dữ liệu (3)" sẽ khớp với môn có tên hiển thị tương ứng.
    - Hệ thống tự động xóa khoảng trắng thừa và không phân biệt hoa thường.
    
    **Quy trình xử lý:**
    1. Nhận diện sinh viên qua **Mã SV** (ưu tiên cao nhất).
    2. Nếu không có Mã SV, nhận diện qua tổ hợp chính xác: **Họ lót** + **Tên** + **Ngày sinh** (Strict Mode).
    3. Duyệt từng cột điểm, tìm môn học tương ứng và cập nhật điểm vào hệ thống.
    """
    service = ScoreService(session)
    result = await service.import_scores(file, current_user)
    return result
