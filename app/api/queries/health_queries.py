from sqlalchemy.orm import Session
from sqlalchemy import text

def check_database_connection(db: Session) -> bool:
    """
    Check if the database connection is working by executing a simple query
    """
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False 