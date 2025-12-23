# Tổng quan hệ thống FSI Academic System Backend

Đây là tài liệu tổng hợp thông tin về hệ thống backend của FSI Academic System, được tạo tự động để giúp hiểu rõ hơn về kiến trúc và các thành phần của hệ thống. Tài liệu này được cập nhật lần cuối vào ngày 20/12/2025.

## 0. Tổng quan hệ thống
**Các chức năng chính bao gồm:**
*   **Xác thực người dùng:** Đăng nhập, đăng xuất với JWT token.
*   **Quản lý người dùng:** Quản lý tài khoản Admin và Teacher với phân quyền rõ ràng.
*   **Quản lý sinh viên:** Nhập danh sách sinh viên qua file CSV, quản lý thông tin sinh viên.
*   **Quản lý học tập:** Quản lý ngành học (Major), khóa học (Intake), lớp học (Class), môn học (Course).
*   **Quản lý điểm số:** Theo dõi và quản lý điểm số của sinh viên theo từng môn học.
*   **Thông báo:** Hệ thống thông báo cho người dùng.
*   **Lịch sử Upload:** Theo dõi lịch sử upload file CSV và các thao tác import dữ liệu.

## 1. Công nghệ sử dụng

*   **Ngôn ngữ**: Python
*   **Framework**: FastAPI
*   **Cơ sở dữ liệu**: PostgreSQL
*   **ORM**: SQLModel (dựa trên Pydantic và SQLAlchemy)
*   **Migration**: Alembic
*   **Xác thực**: JWT (JSON Web Tokens)
*   **Môi trường**: Docker

## 2. Kiến trúc & Cấu trúc thư mục

Hệ thống tuân theo kiến trúc phân lớp (Layered Architecture) để tách biệt rõ ràng các mối quan tâm (Separation of Concerns).

```
backend/
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── alembic/              # Cấu hình và các file migration của Alembic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py           # (Controller) Dependencies cho FastAPI, xử lý xác thực, phân quyền
│   │   ├── main.py           # (Controller) Tập hợp các router
│   │   ├── routes/           # (Controller) Định nghĩa các API endpoint
│   │   │   ├── login.py      # Authentication endpoints
│   │   │   ├── users.py      # User management endpoints
│   │   │   ├── students_upload.py  # CSV upload for students
│   │   │   ├── private.py    # Private/protected endpoints
│   │   │   └── utils.py      # Utility endpoints
│   │   ├── services/         # (Service) Chứa logic nghiệp vụ chính
│   │   │   └── user_service.py
│   │   └── schemas/          # (Data Access) Pydantic schemas cho request/response
│   │       ├── message.py
│   │       ├── token.py
│   │       └── user.py
│   ├── core/                 # Cấu hình cốt lõi của ứng dụng
│   │   ├── config.py         # Cấu hình hệ thống (biến môi trường)
│   │   ├── db.py             # Thiết lập kết nối CSDL
│   │   └── security.py       # Xử lý bảo mật (password, token)
│   ├── models/               # (Data Access) Định nghĩa các model ánh xạ CSDL
│   │   ├── user_model.py
│   │   ├── role_model.py
│   │   ├── major_model.py
│   │   ├── intake_model.py
│   │   ├── class_model.py
│   │   ├── student_model.py
│   │   ├── course_model.py
│   │   ├── score_model.py
│   │   ├── notification_model.py
│   │   └── upload_history_model.py
│   └── tests/                # Unit tests và integration tests
├── init_postgresql.py        # Script khởi tạo database PostgreSQL
├── uploads/                  # Thư mục lưu trữ file CSV upload
└── ...
```

**Luồng xử lý một request điển hình:**
`Request` → `routes/*.py` → `services/*.py` → `models/*.py` → `Cơ sở dữ liệu`
```

**Luồng xử lý một request điển hình:**
`Request` → `routes/*.py` → `services/*.py` → `models/*.py` → `Cơ sở dữ liệu`

## 3. Các thành phần chính

### 3.1. Lớp Controller (Routes & Deps)

*   **`app/api/routes/`**: Chứa các file định nghĩa API Endpoint. Nhiệm vụ chính là:
    *   Tiếp nhận request HTTP.
    *   Sử dụng `dependencies` để lấy session CSDL và người dùng hiện tại.
    *   Khởi tạo lớp `Service` tương ứng.
    *   Gọi phương thức trong `Service` để xử lý logic.
    *   Trả về response cho client.
*   **`app/api/deps.py`**: Cung cấp các dependency dùng chung, quan trọng nhất là `CurrentUser` để lấy thông tin người dùng đã xác thực từ token JWT.

### 3.2. Lớp Service

*   **`app/api/services/`**: Chứa toàn bộ logic nghiệp vụ của ứng dụng.
    *   `UserService`: Xử lý các nghiệp vụ liên quan đến người dùng như tạo, xác thực, lấy thông tin.
    *   Các service này nhận `session` từ `route` để tương tác với CSDL.
    *   **Lưu ý**: Hiện tại chủ yếu có UserService, các service khác cho Student, Course, Score sẽ được thêm vào khi phát triển tiếp.

### 3.3. Lớp Data Access (Models & Schemas)

*   **`app/models/`**: Chỉ chứa các class kế thừa từ `SQLModel` và có `table=True`, đại diện cho các bảng trong CSDL.
    *   `User`: Thông tin người dùng (Admin, Teacher)
    *   `Role`: Vai trò/quyền hạn
    *   `Major`: Ngành học
    *   `Intake`: Khóa học
    *   `Class`: Lớp học
    *   `Student`: Thông tin sinh viên
    *   `Course`: Môn học
    *   `Score`: Điểm số của sinh viên
    *   `Notification`: Thông báo hệ thống
    *   `UploadHistory`: Lịch sử upload CSV
*   **`app/api/schemas/`**: Chứa các class Pydantic/SQLModel (DTOs - Data Transfer Objects) dùng để:
    *   Validate dữ liệu đầu vào của request (vd: `UserCreate`, `StudentCreate`).
    *   Định dạng dữ liệu trả về của response (vd: `UserPublic`, `Token`).
    *   Tách biệt hoàn toàn cấu trúc dữ liệu của API và cấu trúc của CSDL.

### 3.4. Cấu hình & Bảo mật

*   **`app/core/config.py`**: Quản lý tất cả các biến cấu hình từ file `.env`.
*   **`app/core/security.py`**: Chứa các hàm để băm và xác thực mật khẩu, tạo và giải mã token JWT.

## 4. Xác thực và Phân quyền

*   **Xác thực**: Dựa trên JWT. Endpoint `/login/access-token` trả về `access_token`. Client gửi token này trong header `Authorization: Bearer <token>` cho các request cần xác thực.
*   **Phân quyền**:
    *   Dependency `get_current_user` trong `deps.py` giải mã token và lấy ra người dùng.
    *   Hệ thống có 2 vai trò chính (Role):
        *   **Admin (role_id=1)**: Có toàn quyền trên hệ thống, quản lý users, sinh viên, điểm số.
        *   **Teacher (role_id=2)**: Quản lý sinh viên và điểm số trong phạm vi được phân quyền.
    *   Logic kiểm tra vai trò được thực hiện trong các lớp `Service` hoặc thông qua dependencies.

## 5. Cập nhật trong tương lai

Tài liệu này sẽ được cập nhật khi có những thay đổi lớn về logic hoặc kiến trúc của hệ thống. 