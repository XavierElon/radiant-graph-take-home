from .database import Base, engine, get_db

# Create database tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Initialize database on import
init_db()
