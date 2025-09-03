"""
Routes package initialization
"""
from app.routes.user_routes import router as user_router
from app.routes.student_routes import router as student_router

__all__ = ['user_router', 'student_router']