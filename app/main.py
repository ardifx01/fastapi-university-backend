import os
from fastapi import FastAPI
from app.routes.user_routes import router as user_routes
from app.routes.student_routes import router as student_routes
from app.config.database import MongoDB
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(
    title="University Backend API",
    description="Backend API for University Management System",
    version="1.0.0"
)

# Event handlers
@app.on_event("startup")
async def startup_event():
    MongoDB.connect()

@app.on_event("shutdown")
async def shutdown_event():
    MongoDB.close_connection()

# Include routers
app.include_router(user_routes)
app.include_router(student_routes)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "University Backend API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected" if MongoDB.db is not None else "disconnected"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)