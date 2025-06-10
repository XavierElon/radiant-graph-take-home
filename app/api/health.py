from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.health_service import HealthService

router = APIRouter(
    tags=["health"]
)

@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    health_service = HealthService(db)
    return health_service.get_health_status() 