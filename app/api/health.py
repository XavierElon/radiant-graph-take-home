from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db

router = APIRouter(
    tags=["health"]
)

@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Try to make a simple query to verify database connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)} 