import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlmodel import Session

from db.crud.users import users
from db.models import AccountType, Users
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_author(db_session: Session) -> Users:
    """Create a test author"""
    email = "author_users_endpoint@test.com"
    
    # Check if user already exists
    existing_user = users.get_by_email(db_session, email)
    if existing_user:
        return existing_user
    
    author_data = {
        "email": email,
        "password": "password123",
        "first_name": "Test",
        "last_name": "Author",
        "account_type": AccountType.AUTHOR
    }
    
    return users.create(db_session, author_data)


@pytest.fixture
def test_reader(db_session: Session) -> Users:
    """Create a test reader"""
    email = "reader_users_endpoint@test.com"
    
    # Check if user already exists
    existing_user = users.get_by_email(db_session, email)
    if existing_user:
        return existing_user
    
    reader_data = {
        "email": email,
        "password": "password123",
        "first_name": "Test",
        "last_name": "Reader",
        "account_type": AccountType.READER
    }
    
    return users.create(db_session, reader_data)


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


def test_get_users(client, auth_headers, test_author):
    """Test getting all users"""
    response = client.get("/api/v1/users/all", headers=auth_headers)
    assert response.status_code == 200
    
    # Check that at least one user is returned
    assert len(response.json()) > 0
    
    # Find the test author in the response by ID
    test_user_in_response = next(
        (user for user in response.json() 
         if user["id"] == str(test_author.id)), 
        None
    )
    
    # Assert that the test user is in the response and has the correct email
    assert test_user_in_response is not None
    assert test_user_in_response["email"] == test_author.email


def test_get_me(client, auth_headers, test_author):
    """Test getting the current authenticated user"""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(test_author.id)
    assert response.json()["email"] == test_author.email
    assert response.json()["first_name"] == test_author.first_name
    assert response.json()["last_name"] == test_author.last_name
    assert response.json()["account_type"] == AccountType.AUTHOR.value


def test_get_me_as_reader(client, reader_headers, test_reader):
    """Test getting the current authenticated user as a reader"""
    response = client.get("/api/v1/users/me", headers=reader_headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(test_reader.id)
    assert response.json()["email"] == test_reader.email
    assert response.json()["account_type"] == AccountType.READER.value


def test_get_me_unauthenticated(client):
    """Test getting the current user without authentication"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_get_user(client, auth_headers, test_author):
    """Test getting a specific user"""
    response = client.get(
        f"/api/v1/users/{test_author.id}", 
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_author.email
    assert response.json()["account_type"] == AccountType.AUTHOR.value


def test_get_nonexistent_user(client, auth_headers):
    """Test getting a user that doesn't exist"""
    response = client.get(
        f"/api/v1/users/{uuid4()}", 
        headers=auth_headers
    )
    assert response.status_code == 404


def test_get_reader(client, auth_headers, test_reader):
    """Test getting a reader user"""
    response = client.get(
        f"/api/v1/users/{test_reader.id}", 
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_reader.email
    assert response.json()["account_type"] == AccountType.READER.value


def test_get_users_pagination(client, auth_headers, db_session_for_test):
    """Test pagination for getting users"""
    # Create multiple users for testing pagination
    for i in range(3):
        user_data = {
            "email": f"pagination_user{i}@test.com",
            "password": "password123",
            "first_name": f"Pagination{i}",
            "last_name": "User",
            "account_type": AccountType.AUTHOR
        }
        users.create(db_session_for_test, user_data)
    
    # Test with skip parameter
    response = client.get(
        "/api/v1/users/all?skip=1&limit=2", 
        headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) <= 2  # Should return at most 2 users
    
    # Test with limit parameter
    response = client.get(
        "/api/v1/users/all?limit=1", 
        headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1  # Should return exactly 1 user


def test_get_users_unauthenticated(client):
    """Test getting users without authentication (should fail)"""
    response = client.get("/api/v1/users/all")
    assert response.status_code == 401


def test_get_user_unauthenticated(client, test_author):
    """Test getting a specific user without authentication (should fail)"""
    response = client.get(
        f"/api/v1/users/{test_author.id}"
    )
    assert response.status_code == 401 