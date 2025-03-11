import pytest
from sqlmodel import Session, SQLModel
from db.database import engine
# Import all models to ensure they're registered with SQLModel
from db.models import Users, AccountType
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment once per test session"""
    # Create all tables
    SQLModel.metadata.drop_all(engine)  # Drop all tables first to ensure clean state
    SQLModel.metadata.create_all(engine)  # Create all tables
    yield
    # Cleanup after all tests are done
    SQLModel.metadata.drop_all(engine)  # Clean up tables
    
@pytest.fixture(scope="session")
def test_engine():
    """Return engine instance to be reused across tests"""
    return engine

@pytest.fixture(scope="session")
def test_user_data():
    """Base user data for general tests"""
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "account_type": AccountType.READER
    }

@pytest.fixture(scope="session")
def test_author_data():
    """Base author data for tests"""
    return {
        "email": "author@test.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "Author",
        "account_type": AccountType.AUTHOR
    }

@pytest.fixture(scope="session")
def test_reader_data():
    """Base reader data for tests"""
    return {
        "email": "reader@test.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "Reader",
        "account_type": AccountType.READER
    }

@pytest.fixture(scope="session")
def auth_test_user_data():
    """Data for auth-specific test user"""
    return {
        "email": "testauth@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "Auth",
        "account_type": AccountType.READER
    }

@pytest.fixture(scope="session")
def test_user(db_session, test_user_data) -> Users:
    """Create a general test user"""
    from db.crud.users import users
    return users.create(db_session, test_user_data)

@pytest.fixture(scope="session")
def test_author(db_session, test_author_data) -> Users:
    """Create a test author"""
    from db.crud.users import users
    return users.create(db_session, test_author_data)

@pytest.fixture(scope="session")
def test_reader(db_session, test_reader_data) -> Users:
    """Create a test reader"""
    from db.crud.users import users
    return users.create(db_session, test_reader_data)

@pytest.fixture(scope="session")
def auth_test_user(db_session, auth_test_user_data) -> Users:
    """Create a test user specifically for auth tests"""
    from db.crud.users import users
    return users.create(db_session, auth_test_user_data)

@pytest.fixture(scope="session")
def db_session(test_engine):
    """Provide database session that persists data during test run"""
    connection = test_engine.connect()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    connection.close()

@pytest.fixture(scope="function")
def db_session_for_test(db_session):
    """Provide a database session with transaction isolation for each test"""
    # Start a nested transaction
    connection = db_session.connection()
    transaction = connection.begin_nested()
    
    yield db_session
    
    # Rollback the transaction after the test
    transaction.rollback()
    # Clean up the session to ensure it's in a clean state for the next test
    db_session.expire_all()

# Add shared fixtures to reduce duplication across test files

@pytest.fixture
def client():
    """Return a TestClient instance for testing API endpoints"""
    return TestClient(app)

@pytest.fixture
def auth_token(client, test_author):
    """Get authentication token for author through login"""
    response = client.post(
        "/api/v1/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": test_author.email,
            "password": "password123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def reader_token(client, test_reader):
    """Get authentication token for reader through login"""
    response = client.post(
        "/api/v1/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": test_reader.email,
            "password": "password123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    """Create authentication headers with real JWT token for author"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def reader_headers(reader_token):
    """Create authentication headers with real JWT token for reader"""
    return {"Authorization": f"Bearer {reader_token}"} 
