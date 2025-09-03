from pymongo.database import Database
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timedelta
import os

# Models and Utils (Asumsi path ini benar)
from app.config.database import MongoDB
from app.models.user_model import User, UserUpdate
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.response import create_response

class UserService:
    def __init__(self):
        # Inisialisasi koneksi database dan collection
        db: Database = MongoDB.get_database()
        self.collection = db["users"]

    # PENAMBAHAN: Helper function untuk serialisasi data user
    def _serialize_user(self, user_data: dict) -> dict:
        """
        Mengubah format data user dari DB untuk respons API.
        Menghapus field sensitif dan mengubah _id menjadi id.
        """
        if not user_data:
            return None
        
        user_data["id"] = str(user_data["_id"])
        del user_data["_id"]
        
        # Hapus password hash dari respons
        if "hashed_password" in user_data:
            del user_data["hashed_password"]
            
        return user_data

    def create_user(self, user: User) -> dict:
        # Cek jika user dengan email yang sama sudah ada
        if self.collection.find_one({"email": user.email, "is_deleted": False}):
            return create_response(False, "User with this email already exists", None, "DUPLICATE_EMAIL")

        # PERBAIKAN: Gunakan .model_dump() untuk Pydantic v2, bukan .dict()
        user_data = user.model_dump()

        # Hash password sebelum disimpan
        user_data["hashed_password"] = hash_password(user_data["password"])
        del user_data["password"] # Hapus password asli

        # PENAMBAHAN: Tambahkan field standar saat pembuatan
        now = datetime.now()
        user_data["created_at"] = now
        user_data["updated_at"] = now
        user_data["is_deleted"] = False
        user_data["version"] = 1

        # Simpan ke database
        result = self.collection.insert_one(user_data)
        
        # Ambil data yang baru dibuat dari DB untuk respons yang konsisten
        new_user = self.collection.find_one({"_id": result.inserted_id})
        
        return create_response(True, "User created successfully", self._serialize_user(new_user))

    def authenticate_user(self, email: str, password: str) -> dict | None:
        user = self.collection.find_one({"email": email, "is_deleted": False})

        if not user or not verify_password(password, user.get("hashed_password")):
            return None
        
        access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
        
        # Data yang akan di-encode dalam token
        token_data = {"sub": user["email"], "id": str(user["_id"])}

        access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
        
        # PERBAIKAN: Kembalikan dictionary yang lebih informatif
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": self._serialize_user(user)
        }

    def get_user_by_id(self, user_id: str) -> dict:
        # PERBAIKAN: Tangani error ID yang tidak valid secara spesifik
        try:
            obj_id = ObjectId(user_id)
        except InvalidId:
            return create_response(False, "Invalid user ID format", None, "INVALID_ID")
        
        user = self.collection.find_one({"_id": obj_id, "is_deleted": False})
        
        if not user:
            return create_response(False, "User not found", None, "NOT_FOUND")
            
        return create_response(True, "User found", self._serialize_user(user))

    def get_all_users(self, skip: int = 0, limit: int = 10) -> dict:
        query = {"is_deleted": False}
        
        users_cursor = self.collection.find(query).skip(skip).limit(limit)
        users = [self._serialize_user(user) for user in users_cursor]
        
        # PENAMBAHAN: Sertakan total data untuk pagination di frontend
        total_users = self.collection.count_documents(query)

        response_data = {
            "total": total_users,
            "page": (skip // limit) + 1,
            "limit": limit,
            "data": users
        }
        return create_response(True, "Users retrieved successfully", response_data)

    def update_user(self, user_id: str, user_data: UserUpdate) -> dict:
        try:
            obj_id = ObjectId(user_id)
        except InvalidId:
            return create_response(False, "Invalid user ID format", None, "INVALID_ID")
        
        # PERBAIKAN: Gunakan model_dump(exclude_unset=True) untuk hanya mengambil field yang diisi
        update_data = user_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return create_response(False, "No data provided for update", None, "NO_DATA")

        # PENAMBAHAN: Selalu update `updated_at`
        update_data["updated_at"] = datetime.now()

        # Gunakan $inc untuk menaikkan versi secara atomik
        result = self.collection.update_one(
            {"_id": obj_id, "is_deleted": False},
            {
                "$set": update_data,
                "$inc": {"version": 1}
            }
        )

        if result.matched_count == 0:
            return create_response(False, "User not found", None, "NOT_FOUND")
        
        if result.modified_count == 0:
            return create_response(True, "User data is already up to date", None)

        return create_response(True, "User updated successfully")

    def soft_delete_user(self, user_id: str) -> dict:
        try:
            obj_id = ObjectId(user_id)
        except InvalidId:
            return create_response(False, "Invalid user ID format", None, "INVALID_ID")

        # PERBAIKAN KRITIS: Pisahkan operator $set dan $inc
        update_operation = {
            "$set": {
                "is_deleted": True,
                "deleted_at": datetime.now()
            },
            "$inc": {"version": 1}
        }
        
        result = self.collection.update_one(
            {"_id": obj_id, "is_deleted": False},
            update_operation
        )
        
        if result.modified_count == 0:
            return create_response(False, "User not found or already deleted", None, "NOT_FOUND")
            
        return create_response(True, "User deleted successfully")



# from app.config.database import MongoDB
# from app.models.user_model import User, UserInDB, UserResponse, UserUpdate
# from app.utils.security import hash_password, verify_password, create_access_token
# from app.utils.response import create_response
# from datetime import timedelta, datetime
# import os
# from bson import ObjectId

# class UserService:
#     def __init__(self):
#         self.db = MongoDB.get_database()
#         self.collection = self.db["users"]

#     def create_user(self, user: User):
#         # Cek jika user sudah ada
#         if self.collection.find_one({"email": user.email, "is_deleted": False}):
#             return create_response(False, "User already exists", None, "DUPLICATE_EMAIL")
        
#         # Hash password
#         hashed_password = hash_password(user.password)
        
#         # Buat user document
#         user_dict = user.dict()
#         user_dict["hashed_password"] = hashed_password
#         del user_dict["password"]
        
#         # Simpan ke database
#         result = self.collection.insert_one(user_dict)
        
#         # Buat response tanpa password
#         user_response = user_dict.copy()
#         user_response["id"] = str(result.inserted_id)
#         del user_response["hashed_password"]
        
#         return create_response(True, "User created successfully", user_response)
    
#     def authenticate_user(self, email: str, password: str):
#         user = self.collection.find_one({"email": email, "is_deleted": False})
#         if not user or not verify_password(password, user["hashed_password"]):
#             return None
        
#         # Buat access token
#         access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
#         access_token = create_access_token(
#             data={"sub": user["email"], "id": str(user["_id"])}, 
#             expires_delta=access_token_expires
#         )
        
#         return access_token
    
#     def get_user_by_id(self, user_id: str):
#         try:
#             user = self.collection.find_one({"_id": ObjectId(user_id), "is_deleted": False})
#             if user:
#                 user["id"] = str(user["_id"])
#                 del user["_id"]
#                 del user["hashed_password"]
#                 return create_response(True, "User found", user)
#             return create_response(False, "User not found", None, "NOT_FOUND")
#         except:
#             return create_response(False, "Invalid user ID", None, "INVALID_ID")
    
#     def get_all_users(self, skip: int = 0, limit: int = 10):
#         users = list(self.collection.find({"is_deleted": False}).skip(skip).limit(limit))
#         for user in users:
#             user["id"] = str(user["_id"])
#             del user["_id"]
#             del user["hashed_password"]
#         return create_response(True, "Users retrieved successfully", users)
    
#     def update_user(self, user_id: str, user_data: UserUpdate):
#         try:
#             # Dapatkan user current
#             current_user = self.collection.find_one({"_id": ObjectId(user_id), "is_deleted": False})
#             if not current_user:
#                 return create_response(False, "User not found", None, "NOT_FOUND")
            
#             # Update data
#             update_data = {k: v for k, v in user_data.dict().items() if v is not None}
            
#             if not update_data:
#                 return create_response(False, "No data to update", None, "NO_DATA")
            
#             # Increment version
#             update_data["version"] = current_user.get("version", 1) + 1
            
#             result = self.collection.update_one(
#                 {"_id": ObjectId(user_id), "version": current_user.get("version", 1)},
#                 {"$set": update_data}
#             )
            
#             if result.modified_count == 0:
#                 return create_response(False, "User not found or version conflict", None, "VERSION_CONFLICT")
            
#             return create_response(True, "User updated successfully")
#         except:
#             return create_response(False, "Invalid user ID", None, "INVALID_ID")
    
#     def soft_delete_user(self, user_id: str):
#         try:
#             result = self.collection.update_one(
#                 {"_id": ObjectId(user_id), "is_deleted": False},
#                 {"$set": {
#                     "is_deleted": True,
#                     "deleted_at": datetime.now(),
#                     "version": {"$inc": 1}
#                 }}
#             )
            
#             if result.modified_count == 0:
#                 return create_response(False, "User not found", None, "NOT_FOUND")
            
#             return create_response(True, "User deleted successfully")
#         except:
#             return create_response(False, "Invalid user ID", None, "INVALID_ID")