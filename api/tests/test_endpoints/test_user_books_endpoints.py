import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from db.crud.books import books
from db.crud.users import users
from db.models import AccountType, Users
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_author(db_session: Session) -> Users:
    """Create a test author"""
    email = "author_user_books@test.com"
    
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
    email = "reader_user_books@test.com"
    
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
def test_books(db_session_for_test: Session, test_author: Users):
    """Create multiple test books for the author"""
    book_data1 = {
        "title": "Test Book 1",
        "content": "Test Content 1",
        "author_id": test_author.id
    }
    
    book_data2 = {
        "title": "Test Book 2",
        "content": "Test Content 2",
        "author_id": test_author.id
    }
    
    book1 = books.create(db_session_for_test, book_data1)
    book2 = books.create(db_session_for_test, book_data2)
    
    return [book1, book2]


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


def test_get_user_books(client, auth_headers, test_author, test_books):
    """Test getting books authored by the current user"""
    response = client.get("/api/v1/books/user", headers=auth_headers)
    assert response.status_code == 200
    
    # Check that at least two books are returned
    books_list = response.json()
    assert len(books_list) >= 2
    
    # Find the test books in the response by ID
    book_ids = [book["id"] for book in books_list]
    for test_book in test_books:
        assert str(test_book.id) in book_ids
    
    # Check that all books belong to the test author
    for book in books_list:
        assert book["author_id"] == str(test_author.id)


def test_get_user_books_as_reader(client, reader_headers):
    """Test getting books authored by the current user as a reader"""
    # Should return empty list
    response = client.get(
        "/api/v1/books/user", 
        headers=reader_headers
    )
    assert response.status_code == 200
    
    # Check if the response is an empty list
    books_list = response.json()
    assert isinstance(books_list, list)
    assert len(books_list) == 0


def test_get_user_books_unauthenticated(client):
    """Test getting books authored by the current user without auth"""
    response = client.get("/api/v1/books/user")
    assert response.status_code == 401


def test_get_user_books_pagination(client, auth_headers, test_author, test_books):
    """Test pagination for getting user books"""
    # Test with limit parameter
    response = client.get(
        "/api/v1/books/user?limit=1", 
        headers=auth_headers
    )
    assert response.status_code == 200
    # Should return exactly 1 book
    assert len(response.json()) == 1 