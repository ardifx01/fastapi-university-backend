# File init untuk package app
"""
Main application package initialization
"""
from app.main import app

__version__ = "1.0.0"
__author__ = "Asep Trisna Setiawan"
__description__ = "University Bandar Lampung Backend API with FastAPI and MongoDB"

# Import models, services, controllers untuk memudahkan import di其他地方
from app.models import user_model, student_model
from app.services import user_service, student_service
from app.controllers import user_controller, student_controller

__all__ = [
    'app',
    'user_model',
    'student_model',
    'user_service', 
    'student_service',
    'user_controller',
    'student_controller'
]