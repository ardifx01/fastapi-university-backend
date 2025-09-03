from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

def create_response(success: bool, message: str, data: Any = None, error: str = None) -> Dict:
    return {
        "success": success,
        "message": message,
        "data": data,
        "error": error
    }