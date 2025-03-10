import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlmodel import Session

from db.crud.users import users
from db.models import AccountType, Users


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


def test_get_users(client: TestClient, auth_headers, test_author):
    """Test getting all users"""
    response = client.get("/api/v1/users/all", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_me(client: TestClient, auth_headers, test_author):
    """Test getting the current authenticated user"""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_author.email


def test_get_me_as_reader(client: TestClient, reader_headers, test_reader):
    """Test getting the current authenticated user as a reader"""
    response = client.get("/api/v1/users/me", headers=reader_headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_reader.email


def test_get_me_unauthenticated(client: TestClient):
    """Test getting the current user without authentication"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_get_user(client: TestClient, auth_headers, test_author):
    """Test getting a specific user"""
    response = client.get(
        f"/api/v1/users/{test_author.id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_author.email


def test_get_nonexistent_user(client: TestClient, auth_headers):
    """Test getting a user that doesn't exist"""
    response = client.get(
        f"/api/v1/users/{uuid4()}", headers=auth_headers
    )
    assert response.status_code == 404


def test_get_reader(client: TestClient, auth_headers, test_reader):
    """Test getting a reader user"""
    response = client.get(
        f"/api/v1/users/{test_reader.id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_reader.email


def test_get_users_pagination(client: TestClient, auth_headers, db_session):
    """Test pagination for getting users"""
    # Create multiple users for testing pagination
    response = client.get("/api/v1/users/all?skip=1&limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 2

    response = client.get("/api/v1/users/all?limit=1", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


def test_get_users_unauthenticated(client: TestClient):
    """Test getting users without authentication (should fail)"""
    response = client.get("/api/v1/users/all")
    assert response.status_code == 401


def test_get_user_unauthenticated(client: TestClient, test_author):
    """Test getting a specific user without authentication (should fail)"""
    response = client.get(
        f"/api/v1/users/{test_author.id}"
    )
    assert response.status_code == 401 