from sqlalchemy.orm import Session
from ..queries.health_queries import check_database_connection

class HealthService:
    def __init__(self, db: Session):
        self.db = db

    def get_health_status(self) -> dict:
        """
        Get the overall health status of the application
        """
        db_status = check_database_connection(self.db)
        
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected"
        } 