from fastapi import APIRouter
from app.controllers.student_controller import router as student_router

router = APIRouter()
router.include_router(student_router, prefix="/students", tags=["students"])