import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.models import Customer, Address, Order
import logging

# Set up SQL logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Create test database engine
SQLALCHEMY_DATABASE_URL = "postgresql://radiant:radiant123@localhost:5433/radiant_graph_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)  # Enable SQL echo
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        # Clean up after each test
        db.rollback()
        db.close()
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.rollback()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear() 