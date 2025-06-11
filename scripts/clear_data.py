from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL

def clear_data():
    """Clear all data from the database tables."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.begin() as conn:
        # Disable foreign key checks temporarily
        conn.execute(text("SET session_replication_role = 'replica';"))
        
        # Clear tables in correct order (respecting foreign key constraints)
        conn.execute(text("TRUNCATE TABLE orders CASCADE;"))
        conn.execute(text("TRUNCATE TABLE addresses CASCADE;"))
        conn.execute(text("TRUNCATE TABLE customers CASCADE;"))
        
        # Re-enable foreign key checks
        conn.execute(text("SET session_replication_role = 'origin';"))
        
        print("All data cleared successfully!")

if __name__ == "__main__":
    clear_data() 