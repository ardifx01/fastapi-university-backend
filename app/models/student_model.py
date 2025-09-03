import re
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, Annotated

from bson import ObjectId
from pydantic import BaseModel, Field, BeforeValidator, field_validator, ConfigDict

# --- Tipe Kustom untuk ObjectId ---
# Helper function ini akan mengonversi ObjectId dari BSON menjadi string.
def str_object_id(v: any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    # Jika sudah string atau tipe lain, kembalikan apa adanya.
    return v

# Membuat tipe data `PyObjectId` menggunakan Annotated.
# Pydantic akan menjalankan `BeforeValidator` sebelum memvalidasi tipe data sebagai string.
PyObjectId = Annotated[str, BeforeValidator(str_object_id)]


# --- Model untuk Membuat Data Mahasiswa (Payload untuk POST) ---
class Student(BaseModel):
    nim: str = Field(..., min_length=8, max_length=15)
    name: str = Field(..., min_length=3, max_length=100)
    email: str # Validasi akan dilakukan oleh @field_validator di bawah
    study_program: str = Field(..., min_length=3, max_length=100)
    semester: int = Field(..., ge=1, le=14)
    gpa: float = Field(..., ge=0.0, le=4.0)
    created_by: str

    # Field dengan nilai default yang diatur otomatis oleh server
    version: int = Field(default=1, description="Version for optimistic locking")
    guid: str = Field(default_factory=lambda: f"STUDENT-{uuid4()}", description="Global Unique Identifier")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)
    is_deleted: bool = Field(default=False)

    # ✅ Sintaks Pydantic V2 untuk validator
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v


# --- Model untuk Respons API (Mengirim Data ke Klien) ---
class StudentResponse(BaseModel):
    # ✅ Konfigurasi dipindahkan ke dalam model menggunakan model_config
    model_config = ConfigDict(
        populate_by_name=True,      # Izinkan alias (misal: `_id` dari DB ke `id` di model)
        arbitrary_types_allowed=True # Diperlukan untuk proses konversi ObjectId
    )

    # Menggunakan alias `_id` agar cocok dengan field di MongoDB
    id: PyObjectId = Field(alias="_id")
    nim: str
    name: str
    email: str
    study_program: str
    semester: int
    gpa: float
    created_by: str
    version: int
    guid: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# --- Model untuk Memperbarui Data Mahasiswa (Payload untuk PUT/PATCH) ---
class StudentUpdate(BaseModel):
    # Semua field data bersifat opsional untuk update
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[str] = None # Validasi akan dilakukan di bawah
    study_program: Optional[str] = Field(None, min_length=3, max_length=100)
    semester: Optional[int] = Field(None, ge=1, le=14)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    
    # Version wajib disertakan untuk optimistic locking
    version: int = Field(..., description="Current version for optimistic locking")

    # ✅ Sintaks Pydantic V2 untuk validator pada field opsional
    @field_validator('email')
    @classmethod
    def validate_optional_email(cls, v: Optional[str]) -> Optional[str]:
        # Jika email tidak disertakan dalam payload, lewati validasi
        if v is None:
            return v
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v

# from pydantic import BaseModel, Field, validator
# from typing import Optional
# from datetime import datetime
# import re
# from uuid import uuid4

# def str_object_id(v: any) -> str:
#     if isinstance(v, ObjectId):
#         return str(v)
#     return v
# PyObjectId = Annotated[str, BeforeValidator(str_object_id)]

# class Student(BaseModel):
#     nim: str = Field(..., min_length=8, max_length=15)
#     name: str = Field(..., min_length=3, max_length=100)
#     email: str = Field(..., min_length=5, max_length=100)
#     study_program: str = Field(..., min_length=3, max_length=100)
#     semester: int = Field(..., ge=1, le=14)
#     gpa: float = Field(..., ge=0.0, le=4.0)
#     created_by: str
#     version: int = Field(default=1, description="Version for optimistic locking")
#     guid: str = Field(default_factory=lambda: f"STUDENT-{uuid4()}-{datetime.now().year}", description="Global Unique Identifier")
#     created_at: datetime = Field(default_factory=datetime.now)
#     updated_at: Optional[datetime] = None
#     deleted_at: Optional[datetime] = None
#     is_deleted: bool = False

#     @validator('email')
#     def validate_email(cls, v):
#         pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#         if not re.match(pattern, v):
#             raise ValueError('Invalid email format')
#         return v

#     class Config:
#         validate_assignment = True

# class StudentResponse(BaseModel):
#     id:  PyObjectId = Field(alias="_id")
#     nim: str
#     name: str
#     email: str
#     study_program: str
#     semester: int
#     gpa: float
#     created_by: str
#     version: int
#     guid: str
#     created_at: datetime
#     updated_at: Optional[datetime] = None

# class StudentUpdate(BaseModel):
#     name: Optional[str] = Field(None, min_length=3, max_length=100)
#     email: Optional[str] = Field(None, min_length=5, max_length=100)
#     study_program: Optional[str] = Field(None, min_length=3, max_length=100)
#     semester: Optional[int] = Field(None, ge=1, le=14)
#     gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
#     version: int = Field(..., description="Current version for optimistic locking")
#     updated_at: datetime = Field(default_factory=datetime.now)

#     @validator('email')
#     def validate_email(cls, v):
#         if v is None:
#             return v
#         pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#         if not re.match(pattern, v):
#             raise ValueError('Invalid email format')
#         return v

# class Config:
#         # Izinkan populasi model menggunakan alias (agar '_id' bisa diisi ke 'id')
#         populate_by_name = True 
#         # Izinkan tipe data arbitrary seperti ObjectId (meskipun akan dikonversi)
#         arbitrary_types_allowed = True