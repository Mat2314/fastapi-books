import pytest
import os
from sqlmodel import Session, SQLModel
from db.database import engine
# Import all models to ensure they're registered with SQLModel
from db.models import Users, Books  # Add any other models you have

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment once per test session"""
    if os.getenv("TESTING") is None:  # Check if we haven't set up testing env yet
        os.environ["TESTING"] = "True"
        # Create all tables
        SQLModel.metadata.drop_all(engine)  # Drop all tables first to ensure clean state
        SQLModel.metadata.create_all(engine)  # Create all tables
        yield
        # Cleanup after all tests are done
        SQLModel.metadata.drop_all(engine)  # Clean up tables
        os.environ.pop("TESTING", None)
    else:
        yield

@pytest.fixture(scope="session")
def test_engine():
    """Return engine instance to be reused across tests"""
    return engine

@pytest.fixture
def db_session(test_engine):
    """Provide database session per test, with transaction rollback"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close() 
