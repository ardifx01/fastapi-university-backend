from fastapi import APIRouter, HTTPException, Depends, status, Query
from app.models.user_model import User, UserLogin, UserUpdate
from app.services.user_service import UserService
from app.middlewares.auth_middleware import JWTBearer, get_current_user
from app.utils.response import create_response
from fastapi.responses import JSONResponse

router = APIRouter()
user_service = UserService()

#Regsiter Akun
@router.post("/register", response_model=dict)
async def register_user(user: User):
    result = user_service.create_user(user)
    if not result["success"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=result 
        )
    return result

#Login
@router.post("/login", response_model=dict)
async def login_user(user: UserLogin):
    token = user_service.authenticate_user(user.email, user.password)
    if not token:
       # ✅ Buat konten error kustom Anda
        error_content = {"success": False, "message": "Invalid credentials"}
        
        # ✅ Kembalikan JSONResponse dengan status_code, content, dan headers yang sesuai
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_content,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_response(True, "Login successful", token)

@router.get("/{user_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def get_user(user_id: str):
    result = user_service.get_user_by_id(user_id)
    if not result["success"]:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=result
        )
    return result

@router.get("/", response_model=dict, dependencies=[Depends(JWTBearer())])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    result = user_service.get_all_users(skip, limit)
    return result

@router.put("/{user_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def update_user(user_id: str, user_data: UserUpdate, current_user: dict = Depends(get_current_user)):
    result = user_service.update_user(user_id, user_data)
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

@router.delete("/{user_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    result = user_service.soft_delete_user(user_id)
    if not result["success"]:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=result
        )
    return result