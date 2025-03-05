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


def test_get_authors(client, auth_headers, test_author):
    """Test getting all authors"""
    response = client.get("/api/v1/users/authors", headers=auth_headers)
    assert response.status_code == 200
    
    # Check that at least one author is returned
    assert len(response.json()) > 0
    
    # Find the test author in the response by ID
    test_author_in_response = next(
        (author for author in response.json() 
         if author["id"] == str(test_author.id)), 
        None
    )
    
    # Assert that the test author is in the response and has the correct email
    assert test_author_in_response is not None
    assert test_author_in_response["email"] == test_author.email


def test_get_author(client, auth_headers, test_author):
    """Test getting a specific author"""
    response = client.get(
        f"/api/v1/users/authors/{test_author.id}", 
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_author.email
    assert response.json()["account_type"] == AccountType.AUTHOR.value


def test_get_nonexistent_author(client, auth_headers):
    """Test getting an author that doesn't exist"""
    response = client.get(
        f"/api/v1/users/authors/{uuid4()}", 
        headers=auth_headers
    )
    assert response.status_code == 404


def test_get_reader_as_author(client, auth_headers, test_reader):
    """Test getting a reader as an author (should fail with 400 Bad Request)"""
    response = client.get(
        f"/api/v1/users/authors/{test_reader.id}", 
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "User is not an author" in response.json()["detail"]


def test_get_authors_pagination(client, auth_headers, db_session_for_test):
    """Test pagination for getting authors"""
    # Create multiple authors for testing pagination
    for i in range(3):
        author_data = {
            "email": f"pagination_author{i}@test.com",
            "password": "password123",
            "first_name": f"Pagination{i}",
            "last_name": "Author",
            "account_type": AccountType.AUTHOR
        }
        users.create(db_session_for_test, author_data)
    
    # Test with skip parameter
    response = client.get("/api/v1/users/authors?skip=1&limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) <= 2  # Should return at most 2 authors
    
    # Test with limit parameter
    response = client.get("/api/v1/users/authors?limit=1", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1  # Should return exactly 1 author


def test_get_authors_unauthenticated(client):
    """Test getting authors without authentication (should fail)"""
    response = client.get("/api/v1/users/authors")
    assert response.status_code == 401


def test_get_author_unauthenticated(client, test_author):
    """Test getting a specific author without authentication (should fail)"""
    response = client.get(
        f"/api/v1/users/authors/{test_author.id}"
    )
    assert response.status_code == 401 