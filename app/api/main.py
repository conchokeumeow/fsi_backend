from fastapi import APIRouter

from app.api.routes import login, students_upload, scores_upload

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(students_upload.router, prefix="/students", tags=["students"])
api_router.include_router(scores_upload.router, prefix="/scores", tags=["scores"])
