
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from io import BytesIO

from fastapi import UploadFile, HTTPException
from sqlmodel import Session, select

from app.models.student_model import Student
from app.models.course_model import Course
from app.models.score_model import Score
from app.models.upload_history_model import UploadHistory
from app.models.user_model import User

class ScoreService:
    """Service xử lý các nghiệp vụ liên quan đến import điểm"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def import_scores(
        self, 
        file: UploadFile, 
        current_user: User
    ) -> UploadHistory:
        """
        Import điểm từ file Excel hoặc CSV.
        
        Cấu trúc file:
        - Mỗi dòng là một Sinh viên.
        - Các cột (trừ thông tin SV) là các Môn học.
        - Giao điểm dòng/cột là Điểm số.
        
        Quy trình xử lý:
        1. Validate: Kiểm tra định dạng file (.xlsx, .xls, .csv).
        2. History: Tạo bản ghi lịch sử upload (trạng thái PROCESSING).
        3. Read: Đọc file vào DataFrame, tự động xử lý encoding cho CSV.
        4. Normalize: Chuẩn hóa tên cột (lowercase, xóa khoảng trắng thừa).
        5. Process: Duyệt từng dòng để tìm sinh viên và map điểm vào môn học.
        6. Result: Cập nhật kết quả vào lịch sử upload.
        """
        self._validate_file(file)
        
        upload_history = self._create_upload_history(file.filename, current_user.user_id)
        
        try:
            # 1. Đọc file thành DataFrame
            df = await self._read_file(file)
            
            # 2. Chuẩn hóa tiêu đề cột
            # Chuyển về chữ thường và xóa khoảng trắng ở 2 đầu
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # Quan trọng: Xóa khoảng trắng thừa giữa các từ để khớp với course_display_name trong DB
            # Ví dụ: "Cơ sở   dữ liệu" -> "cơ sở dữ liệu"
            import re
            df.columns = [re.sub(r'\s+', ' ', col) for col in df.columns]
            
            # 3. Xử lý dữ liệu
            result = await self._process_dataframe(df, current_user)
            
            self._update_history_success(upload_history, result)
            
        except Exception as e:
            self._update_history_failure(upload_history, str(e))
            raise e
        
        finally:
            self.session.commit()
            self.session.refresh(upload_history)
        
        return upload_history

    def _validate_file(self, file: UploadFile) -> None:
        """Kiểm tra tên file và đuôi file hợp lệ"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Tên file là bắt buộc")
        
        valid_extensions = ['.xlsx', '.xls', '.csv']
        if not any(file.filename.endswith(ext) for ext in valid_extensions):
             raise HTTPException(status_code=400, detail="Định dạng file không hợp lệ. Vui lòng upload file .xlsx, .xls hoặc .csv")

    def _create_upload_history(self, filename: str, user_id: int) -> UploadHistory:
        """Tạo bản ghi theo dõi tiến trình upload"""
        history = UploadHistory(
            file_name=filename,
            created_by_id=user_id,
            status="PROCESSING"
        )
        self.session.add(history)
        self.session.commit()
        self.session.refresh(history)
        return history

    async def _read_file(self, file: UploadFile) -> pd.DataFrame:
        """Đọc nội dung file vào Pandas DataFrame, hỗ trợ nhiều bảng mã cho CSV"""
        contents = await file.read()
        file_bytes = BytesIO(contents)
        
        if file.filename.endswith('.csv'):
            # Thử các bảng mã phổ biến, đặc biệt là các bảng mã tiếng Việt
            encodings = ['utf-8-sig', 'utf-8', 'cp1258', 'cp1252'] # cp1258 thường dùng cho tiếng Việt cũ
            
            for encoding in encodings:
                try:
                    file_bytes.seek(0)
                    return pd.read_csv(file_bytes, encoding=encoding)
                except UnicodeDecodeError:
                    continue
            
            # Nếu thất bại hết thì thử mặc định của pandas
            file_bytes.seek(0)
            return pd.read_csv(file_bytes)
        else:
            return pd.read_excel(file_bytes)

    async def _process_dataframe(self, df: pd.DataFrame, user: User) -> Dict[str, int]:
        """
        Hàm xử lý chính: Duyệt qua từng dòng dữ liệu.
        
        Chiến lược:
        1. Tách các cột 'Thông tin sinh viên' và cột 'Môn học' (còn lại).
        2. Cache danh sách môn học từ DB để tra cứu nhanh (dùng course_display_name).
        3. Duyệt từng dòng:
           - Tìm sinh viên (theo ID hoặc Họ + Tên + Ngày sinh).
           - Duyệt từng cột môn học, lấy điểm số.
           - Upsert điểm (Insert hoặc Update) vào DB.
        """
        total_rows = len(df)
        success_count = 0
        failure_count = 0
        
        # Danh sách các tên cột phổ biến chứa thông tin sinh viên (để loại trừ khỏi danh sách môn học)
        student_info_cols = [
            'stt', 'no.', 'no',
            'lớp', 'class', 'class_id',
            'họ lót', 'họ đệm', 'last name', 'surname',
            'tên', 'first name', 'name',
            'họ và tên', 'họ tên', 'fullname', 'full name',
            'ngày sinh', 'dob', 'date of birth',
            'mã sv', 'mã sinh viên', 'student_id', 'id'
        ]
        
        # Cột Môn học là các cột KHÔNG nằm trong danh sách trên
        subject_cols = [c for c in df.columns if c not in student_info_cols]
        
        # Tải trước danh sách môn học vào RAM để tra cứu nhanh (Caching)
        # Map: course_display_name (lowercase) -> course_id
        # Ví dụ: "cơ sở dữ liệu (3)" -> 123
        courses = self.session.exec(select(Course)).all()
        course_map = {}
        
        for c in courses:
            # Ưu tiên map theo tên hiển thị (có kèm tín chỉ)
            if c.course_display_name:
                course_map[c.course_display_name.strip().lower()] = c.course_id
            # Fallback: map theo tên gốc
            course_map[c.course_name.strip().lower()] = c.course_id

        for index, row in df.iterrows():
            try:
                # Tìm sinh viên tương ứng với dòng hiện tại
                student = self._find_student(row)
                if not student:
                    # Nếu không tìm thấy sinh viên -> Bỏ qua dòng này (có thể log lại)
                    failure_count += 1
                    continue
                
                # Duyệt qua từng cột môn học để lấy điểm
                for col in subject_cols:
                    score_val = row[col]
                    if pd.isna(score_val):
                        continue # Bỏ qua nếu ô điểm trống
                    
                    # Tìm ID môn học dựa trên tên cột (tên cột đã được normalize)
                    course_id = course_map.get(col)
                    
                    if not course_id:
                         # Nếu tên cột không khớp với môn nào trong DB -> Log warn và bỏ qua
                         continue
                        
                    self._upsert_score(student.student_id, course_id, float(score_val))
                
                success_count += 1
                
            except Exception as e:
                print(f"Lỗi tại dòng {index}: {e}")
                failure_count += 1
        
        return {
            "total_processed": total_rows,
            "success_count": success_count,
            "failure_count": failure_count
        }

    def _find_student(self, row: pd.Series) -> Optional[Student]:
        """
        Tìm kiếm sinh viên trong DB dựa trên dữ liệu dòng (row).
        
        Thứ tự ưu tiên:
        1. Tìm theo Mã SV (nếu có cột ID).
        2. Tìm theo (Họ lót + Tên + Ngày sinh) - Matching chính xác tuyệt đối (Strict).
        3. Fallback: Tìm theo Họ tên đầy đủ (+ ngày sinh nếu có).
        """
        
        # Ưu tiên 1: Tìm theo Mã Sinh Viên (ID)
        sid_cols = ['mã sv', 'mã sinh viên', 'student_id', 'id']
        for c in sid_cols:
            if c in row.index and not pd.isna(row[c]):
                sid = str(row[c]).strip()
                student = self.session.exec(select(Student).where(Student.student_id == sid)).first()
                if student:
                    return student
        
        # Ưu tiên 2: Tìm theo Họ tên + Ngày sinh (Strict Mode)
        # Yêu cầu: Phải có đủ cột 'Họ lót', 'Tên' và 'Ngày sinh'
        fullname = None
        if 'họ lót' in row.index and 'tên' in row.index:
            ho_lot = str(row['họ lót']).strip()
            ten = str(row['tên']).strip()
            fullname_combined = f"{ho_lot} {ten}"
            
            # Kiểm tra ngày sinh
            dob_val = None
            dob_cols = ['ngày sinh', 'dob', 'date of birth']
            for c in dob_cols:
                if c in row.index and not pd.isna(row[c]):
                    dob_val = row[c]
                    break
            
            if dob_val:
                # Thử parse ngày sinh theo nhiều định dạng để khớp chính xác
                # Xử lý trường hợp nhập nhằng như 1/3/2000 (3 tháng 1 hay 1 tháng 3?)
                
                # Các format sẽ thử lần lượt
                date_formats = ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d"]
                possible_dates = set()
                
                date_str = str(dob_val).strip()
                for fmt in date_formats:
                    try:
                        dt = datetime.strptime(date_str, fmt).date()
                        possible_dates.add(dt)
                    except ValueError:
                        continue
                
                # Query DB với từng ngày có thể
                found_student = None
                for p_date in possible_dates:
                    # Query chính xác: Tên == fullname AND Ngày sinh == p_date
                    student = self.session.exec(
                        select(Student).where(
                            Student.fullname == fullname_combined,
                            Student.dob == p_date
                        )
                    ).first()
                    if student:
                        found_student = student
                        break
                        
                if found_student:
                    return found_student
        
        # Fallback: Logic tìm kiếm lỏng hơn (chỉ dùng khi Strict Mode thất bại)
        if 'fullname' in row.index:
            fullname = str(row['fullname']).strip()
        elif 'họ và tên' in row.index:
            fullname = str(row['họ và tên']).strip()
        elif 'họ tên' in row.index:
            fullname = str(row['họ tên']).strip()
        elif 'họ lót' in row.index and 'tên' in row.index:
            fullname = f"{str(row['họ lót']).strip()} {str(row['tên']).strip()}"
        
        if not fullname:
            return None
            
        query = select(Student).where(Student.fullname == fullname)
        
        # Nếu có ngày sinh, thêm điều kiện vào query
        dob_val = None
        dob_cols = ['ngày sinh', 'dob', 'date of birth']
        for c in dob_cols:
            if c in row.index and not pd.isna(row[c]):
                dob_val = row[c]
                break
        
        if dob_val:
            parsed_dob = self._parse_date(dob_val)
            if parsed_dob:
                query = query.where(Student.dob == parsed_dob)
                
        students = self.session.exec(query).all()
        
        # Chỉ trả về nếu tìm thấy duy nhất 1 sinh viên khớp
        if len(students) == 1:
            return students[0]
        
        # Nếu tìm thấy nhiều người trùng tên (và không phân biệt được bằng DOB), trả về None để an toàn
        return None

    def _upsert_score(self, student_id: str, course_id: int, score_val: float):
        """
        Cập nhật hoặc Thêm mới điểm số (Upsert).
        Nếu điểm của SV này cho Môn này đã có -> Cập nhật.
        Nếu chưa có -> Thêm mới.
        """
        existing = self.session.exec(
            select(Score).where(
                Score.student_id == student_id,
                Score.course_id == course_id
            )
        ).first()
        
        if existing:
            existing.score = score_val
            self.session.add(existing)
        else:
            new_score = Score(
                student_id=student_id,
                course_id=course_id,
                score=score_val
            )
            self.session.add(new_score)

    def _parse_date(self, val: Any):
        """Hàm helper để parse ngày tháng từ nhiều định dạng khác nhau"""
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, pd.Timestamp):
            return val.date()
            
        date_str = str(val).strip()
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    def _update_history_success(self, history: UploadHistory, result: Dict[str, int]):
        """Cập nhật trạng thái thành công cho lịch sử upload"""
        history.status = "COMPLETED"
        history.total_processed = result["total_processed"]
        history.success_count = result["success_count"]
        history.failure_count = result["failure_count"]
        self.session.add(history)

    def _update_history_failure(self, history: UploadHistory, error_msg: str):
        """Cập nhật trạng thái thất bại cho lịch sử upload"""
        history.status = "FAILED"
        history.error_message = error_msg
        self.session.add(history)
