from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from app.config.database import MongoDB
from app.models.student_model import Student, StudentUpdate
from app.utils.response import create_response

class StudentService:
    """Service layer for student-related operations."""

    def __init__(self):
        """Initializes the database connection and collection."""
        self.db = MongoDB.get_database()
        self.collection = self.db["students"]
        # 💡 Praktik Terbaik: Buat index untuk memastikan keunikan NIM dan performa query
        self.collection.create_index([("nim", 1)], unique=True, partialFilterExpression={"is_deleted": False})

    def create_student(self, student: Student):
        """Creates a new student in the database."""
        try:
            # ✅ Pydantic v2 menggunakan .model_dump() bukan .dict()
            student_dict = student.model_dump()
            
            # 💡 Penambahan field standar saat pembuatan
            student_dict["created_at"] = datetime.now(timezone.utc)
            student_dict["updated_at"] = datetime.now(timezone.utc)
            
            result = self.collection.insert_one(student_dict)
            
            # ✅ Format respons setelah berhasil
            created_student = self.collection.find_one({"_id": result.inserted_id})
            created_student["id"] = str(created_student["_id"])
            
            return create_response(True, "Student created successfully", created_student)
        
        except DuplicateKeyError:
            # ✅ Lebih andal menangani duplikat dari index database
            return create_response(False, "Student with this NIM already exists", None, "DUPLICATE_NIM")

    def get_student_by_id(self, student_id: str):
        """Retrieves a single student by their ID."""
        try:
            obj_id = ObjectId(student_id)
            student = self.collection.find_one({"_id": obj_id, "is_deleted": False})
            
            if student:
                student["id"] = str(student["_id"])
                return create_response(True, "Student found", student)
            
            return create_response(False, "Student not found", None, "NOT_FOUND")
        
        except InvalidId:
            # ✅ Lebih spesifik menangani error ID yang tidak valid
            return create_response(False, "Invalid student ID format", None, "INVALID_ID")

    def get_all_students(self, skip: int = 0, limit: int = 10, filters: dict = None):
        """Retrieves a paginated list of students."""
        query = {"is_deleted": False}
        if filters:
            # ✅ Memastikan filter tidak menimpa query utama
            query.update({k: v for k, v in filters.items() if k != "is_deleted"})
        
        cursor = self.collection.find(query).skip(skip).limit(limit)
        students = list(cursor)
        
        for student in students:
            student["id"] = str(student["_id"])
        
        total = self.collection.count_documents(query)
        
        data = {
            "items": students,
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit
        }
        return create_response(True, "Students retrieved successfully", data)

    def update_student(self, student_id: str, student_data: StudentUpdate):
        """Updates an existing student's data with version control."""
        try:
            obj_id = ObjectId(student_id)
            
            # ✅ .model_dump(exclude_unset=True) hanya mengambil field yang dikirim klien
            update_fields = student_data.model_dump(exclude_unset=True)
            
            if not update_fields or all(k == "version" for k in update_fields):
                return create_response(False, "No data provided to update", None, "NO_DATA")

            # 💡 Pisahkan 'version' dari data yang akan di-update
            client_version = update_fields.pop("version", None)
            if client_version is None:
                return create_response(False, "Version number is required for updates", None, "VERSION_REQUIRED")
                
            # ✅ Gunakan find_one_and_update untuk operasi atomik (lebih aman)
            updated_student = self.collection.find_one_and_update(
                {"_id": obj_id, "is_deleted": False, "version": client_version},
                {
                    "$set": {**update_fields, "updated_at": datetime.now(timezone.utc)},
                    "$inc": {"version": 1}
                },
                return_document=True  # Mengembalikan dokumen setelah di-update
            )
            
            if updated_student:
                updated_student["id"] = str(updated_student["_id"])
                return create_response(True, "Student updated successfully", updated_student)
            
            # Jika gagal, cek penyebabnya
            existing_student = self.collection.find_one({"_id": obj_id, "is_deleted": False})
            if not existing_student:
                return create_response(False, "Student not found", None, "NOT_FOUND")
            else:
                return create_response(False, "Update failed due to version conflict", None, "VERSION_CONFLICT")
        
        except InvalidId:
            return create_response(False, "Invalid student ID format", None, "INVALID_ID")

    def soft_delete_student(self, student_id: str):
        """Soft deletes a student by setting 'is_deleted' to True."""
        try:
            obj_id = ObjectId(student_id)
            
            result = self.collection.update_one(
                {"_id": obj_id, "is_deleted": False},
                {
                    "$set": {
                        "is_deleted": True,
                        "deleted_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    },
                    "$inc": {"version": 1} # Tetap increment versi saat soft delete
                }
            )
            
            if result.modified_count == 0:
                return create_response(False, "Student not found or already deleted", None, "NOT_FOUND")
            
            return create_response(True, "Student deleted successfully", None)
        
        except InvalidId:
            return create_response(False, "Invalid student ID format", None, "INVALID_ID")

# from app.config.database import MongoDB
# from app.models.student_model import Student, StudentResponse, StudentUpdate
# from app.utils.response import create_response
# from bson import ObjectId
# from datetime import datetime

# class StudentService:
#     def __init__(self):
#         self.db = MongoDB.get_database()
#         self.collection = self.db["students"]

#     def create_student(self, student: Student):
#         # Cek jika NIM sudah ada
#         if self.collection.find_one({"nim": student.nim, "is_deleted": False}):
#             return create_response(False, "Student with this NIM already exists", None, "DUPLICATE_NIM")
        
#         # Simpan ke database
#         student_dict = student.dict()
#         result = self.collection.insert_one(student_dict)
        
#         # Buat response
#         student_response = student_dict.copy()
#         student_response["id"] = str(result.inserted_id)
        
#         return create_response(True, "Student created successfully", student_response)
    
#     def get_student_by_id(self, student_id: str):
#         try:
#             student = self.collection.find_one({"_id": ObjectId(student_id), "is_deleted": False})
#             if student:
#                 student["id"] = str(student["_id"])
#                 del student["_id"]
#                 return create_response(True, "Student found", student)
#             return create_response(False, "Student not found", None, "NOT_FOUND")
#         except:
#             return create_response(False, "Invalid student ID", None, "INVALID_ID")
    
#     def get_all_students(self, skip: int = 0, limit: int = 10, filters: dict = None):
#         query = {"is_deleted": False}
#         if filters:
#             query.update(filters)
            
#         students = list(self.collection.find(query).skip(skip).limit(limit))
#         for student in students:
#             student["id"] = str(student["_id"])
#             del student["_id"]
        
#         total = self.collection.count_documents(query)
        
#         result = {
#             "students": students,
#             "total": total,
#             "skip": skip,
#             "limit": limit
#         }
        
#         return create_response(True, "Students retrieved successfully", result)
    
#     def update_student(self, student_id: str, student_data: StudentUpdate):
#         try:
#             # Dapatkan student current
#             current_student = self.collection.find_one({"_id": ObjectId(student_id), "is_deleted": False})
#             if not current_student:
#                 return create_response(False, "Student not found", None, "NOT_FOUND")
            
#             # Validasi version
#             if student_data.version != current_student.get("version", 1):
#                 return create_response(False, "Version conflict", None, "VERSION_CONFLICT")
            
#             # Update data
#             update_data = {k: v for k, v in student_data.dict().items() if v is not None and k != "version"}
            
#             if not update_data:
#                 return create_response(False, "No data to update", None, "NO_DATA")
            
#             # Increment version
#             update_data["version"] = current_student.get("version", 1) + 1
            
#             result = self.collection.update_one(
#                 {"_id": ObjectId(student_id), "version": student_data.version},
#                 {"$set": update_data}
#             )
            
#             if result.modified_count == 0:
#                 return create_response(False, "Student not found or version conflict", None, "VERSION_CONFLICT")
            
#             return create_response(True, "Student updated successfully")
#         except:
#             return create_response(False, "Invalid student ID", None, "INVALID_ID")
    
#     def soft_delete_student(self, student_id: str):
#         try:
#             result = self.collection.update_one(
#                 {"_id": ObjectId(student_id), "is_deleted": False},
#                 {"$set": {
#                     "is_deleted": True,
#                     "deleted_at": datetime.now(),
#                     "version": {"$inc": 1}
#                 }}
#             )
            
#             if result.modified_count == 0:
#                 return create_response(False, "Student not found", None, "NOT_FOUND")
            
#             return create_response(True, "Student deleted successfully")
#         except:
#             return create_response(False, "Invalid student ID", None, "INVALID_ID")