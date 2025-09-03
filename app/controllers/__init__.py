"""
Controllers package initialization
"""
from app.controllers.user_controller import router as user_router
from app.controllers.student_controller import router as student_router

__all__ = ['user_router', 'student_router']