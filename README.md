# Backend MVC University Management System

Sebuah RESTful API yang dibangun menggunakan **Python**, **FastAPI**, dan **MongoDB** untuk mengelola data user dan mahasiswa dalam sistem manajemen universitas.

---

## Fitur Utama

- **Manajemen User (CRUD)**: Buat, baca, perbarui, dan hapus data user.
- **Manajemen Mahasiswa (CRUD)**: Kelola data mahasiswa yang terhubung dengan user.
- **Autentikasi JWT**: Semua endpoint (kecuali login/register) diamankan menggunakan JSON Web Token.
- **Soft Delete**: Penghapusan data tidak menghapus secara fisik tetapi menandai sebagai terhapus.
- **Versioning & Optimistic Locking**: Setiap perubahan data dilacak dengan version number untuk mencegah conflict.
- **GUID Generation**: Setiap data memiliki Global Unique Identifier dengan format USER/STUDENT-uuid-tahun.
- **Paginasi & Filtering**: Dukungan paginasi dan filtering pada endpoint yang mengembalikan daftar data.
- **Validasi Input**: Validasi data masuk secara otomatis menggunakan Pydantic models.
- **Dokumentasi API (Swagger/ReDoc)**: Dokumentasi interaktif tersedia secara otomatis.

---

## Teknologi yang Digunakan

- **Backend**: FastAPI
- **Database**: MongoDB
- **ODM**: PyMongo
- **Bahasa**: Python 3.8+
- **Autentikasi**: JWT dengan bcrypt hashing
- **Validation**: Pydantic

---

## Instalasi & Menjalankan Proyek

### Prasyarat

- Python (v3.8 atau lebih baru)
- MongoDB (server lokal atau Atlas)

### Langkah-langkah Instalasi

1. **Clone repository ini:**
```
git clone https://github.com/Aseptrisna/fastapi-university-backend.git
cd fastapi-university-backend
```

2. **Buat virtual environment:**
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. **Install semua dependency:**
```
pip install -r requirements.txt
```

4. **Konfigurasi Environment Variables:**
Buat file `.env` di direktori root proyek:

```
# Konfigurasi Database
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=university_db

# Konfigurasi JWT (JSON Web Token)
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Sesuaikan nilai `MONGODB_URI` dan `JWT_SECRET_KEY` sesuai dengan konfigurasi Anda.

### Menjalankan Aplikasi

- **Mode Development (dengan hot-reload):**
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 7867
```

Aplikasi akan berjalan di `http://localhost:7867`.

- **Mode Production:**
```
python -m app.main
```

### Mengakses Dokumentasi API

Setelah server berjalan, buka browser dan akses URL berikut untuk melihat dokumentasi:

- **Swagger UI**: `http://localhost:7867/docs`
- **ReDoc**: `http://localhost:7867/redoc`

---

## Dokumentasi API Endpoint

### Autentikasi

| Metode | Endpoint | Deskripsi | Auth Required |
| ------ | -------- | --------- | ------------- |
| POST | `/users/register` | Mendaftarkan user baru | ❌ |
| POST | `/users/login` | Login user dan mendapatkan JWT token | ❌ |

### Modul User (`/users`)

Semua endpoint user membutuhkan Header `Authorization: Bearer <token>`.

| Metode | Endpoint | Deskripsi |
| ------ | -------- | --------- |
| GET | `/users` | Mendapatkan daftar semua user (dengan paginasi) |
| GET | `/users/{user_id}` | Mendapatkan detail user berdasarkan ID |
| PUT | `/users/{user_id}` | Memperbarui data user berdasarkan ID |
| DELETE | `/users/{user_id}` | Menghapus (soft delete) user berdasarkan ID |

### Modul Mahasiswa (`/students`)

Semua endpoint mahasiswa membutuhkan Header `Authorization: Bearer <token>`.

| Metode | Endpoint | Deskripsi |
| ------ | -------- | --------- |
| POST | `/students` | Membuat data mahasiswa baru |
| GET | `/students` | Mendapatkan daftar mahasiswa (dengan filter dan paginasi) |
| GET | `/students/{student_id}` | Mendapatkan detail mahasiswa berdasarkan ID |
| PUT | `/students/{student_id}` | Memperbarui data mahasiswa berdasarkan ID |
| DELETE | `/students/{student_id}` | Menghapus (soft delete) mahasiswa berdasarkan ID |

---

## Contoh Request

### 1. Registrasi User
```
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "password123",
    "full_name": "John Doe"
  }'
```

### 2. Login
```
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

### 3. Membuat Data Mahasiswa (dengan JWT Token)
```
curl -X POST "http://localhost:8000/students/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -d '{
    "nim": "12345678",
    "name": "Alice Smith",
    "email": "alice@example.com",
    "study_program": "Computer Science",
    "semester": 5,
    "gpa": 3.75
  }'
```

### 4. Mendapatkan Data Mahasiswa dengan Filter
```
curl -X GET "http://localhost:8000/students/?study_program=Computer+Science&semester=5" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

---

## Struktur Data

### User Model
```
{
  "id": "ObjectId",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "is_active": "boolean",
  "version": "integer",
  "guid": "USER-uuid-tahun",
  "created_at": "datetime",
  "updated_at": "datetime",
  "deleted_at": "datetime",
  "is_deleted": "boolean"
}
```

### Student Model
```
{
  "id": "ObjectId",
  "nim": "string",
  "name": "string",
  "email": "string",
  "study_program": "string",
  "semester": "integer",
  "gpa": "float",
  "created_by": "string",
  "version": "integer",
  "guid": "STUDENT-uuid-tahun",
  "created_at": "datetime",
  "updated_at": "datetime",
  "deleted_at": "datetime",
  "is_deleted": "boolean"
}
```

---

## Autentikasi & Authorization

1. User mendaftar dengan username, email, dan password
2. Password di-hash menggunakan bcrypt sebelum disimpan
3. User login dengan email dan password
4. Server verifikasi credentials dan generate JWT token
5. Client menggunakan token di header Authorization untuk akses endpoint protected

---

## Error Handling

API mengembalikan response standar:

```
{
  "success": false,
  "message": "Error message",
  "data": null,
  "error": "ERROR_CODE"
}
```

### Kode Error yang Umum:
- VALIDATION_ERROR - Data input tidak valid
- DUPLICATE_EMAIL - Email sudah terdaftar
- DUPLICATE_NIM - NIM sudah terdaftar
- NOT_FOUND - Data tidak ditemukan
- VERSION_CONFLICT - Konflik version pada optimistic locking
- INVALID_CREDENTIALS - Email atau password salah

---

## Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT. Lihat file LICENSE untuk detail lebih lanjut.

---

## Berkontribusi

1. Fork repository
2. Buat feature branch (git checkout -b feature/amazing-feature)
3. Commit changes (git commit -m 'Add amazing feature')
4. Push to branch (git push origin feature/amazing-feature)
5. Open Pull Request

---

## Status Project

Python 3.8+ | FastAPI 0.104 | MongoDB 6.0+ | License MIT

## Support

Jika Anda memiliki pertanyaan atau masalah, silakan buka issue di repository atau hubungi maintainer.