from fastapi import APIRouter, HTTPException, Depends, Query, status
from app.models.student_model import Student, StudentUpdate
from app.services.student_service import StudentService
from app.middlewares.auth_middleware import JWTBearer, get_current_user
from app.utils.response import create_response
from typing import Optional
from fastapi.responses import JSONResponse

router = APIRouter()
student_service = StudentService()

@router.post("/create", response_model=dict, dependencies=[Depends(JWTBearer())])
async def create_student(student: Student, current_user: dict = Depends(get_current_user)):
    # Set created_by dengan ID user yang sedang login
    student.created_by = current_user["id"]
    
    result = student_service.create_student(student)
    if not result["success"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=result 
        )
    return result

@router.get("/{student_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def get_student(student_id: str):
    result = student_service.get_student_by_id(student_id)
    if not result["success"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=result 
        )
    return result

@router.get("/", response_model=dict, dependencies=[Depends(JWTBearer())])
async def get_all_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    study_program: Optional[str] = None,
    semester: Optional[int] = None
):
    filters = {}
    if study_program:
        filters["study_program"] = study_program
    if semester:
        filters["semester"] = semester
        
    result = student_service.get_all_students(skip, limit, filters)
    return result

@router.put("/{student_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def update_student(student_id: str, student_data: StudentUpdate):
    result = student_service.update_student(student_id, student_data)
    if not result["success"]:
        if result["error"] == "VERSION_CONFLICT":
            # ✅ Kembalikan JSONResponse dengan status 409
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=result
            )
        # ✅ Kembalikan JSONResponse dengan status 404 sebagai default error
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=result
        )
    return result

@router.delete("/{student_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def delete_student(student_id: str, current_user: dict = Depends(get_current_user)):
    result = student_service.soft_delete_student(student_id)
    if not result["success"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=result 
        )
    return result