from sqlmodel import SQLModel


class UserPublic(SQLModel):
    user_id: int
    email: str
    fullname: str | None = None
    is_active: bool = True
