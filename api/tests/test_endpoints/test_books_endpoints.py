import pytest
from uuid import uuid4
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
    email = "author_endpoint@test.com"
    
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
    email = "reader_endpoint@test.com"
    
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
def test_book(db_session_for_test: Session, test_author: Users):
    """Create a test book"""
    book_data = {
        "title": "Test Book",
        "content": "Test Content",
        "author_id": test_author.id
    }
    
    return books.create(db_session_for_test, book_data)

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

def test_get_books(client, auth_headers, test_book):
    """Test getting all books"""
    response = client.get("/api/v1/books", headers=auth_headers)
    assert response.status_code == 200
    
    # Check that at least one book is returned
    assert len(response.json()) > 0
    
    # Find the test book in the response by ID
    test_book_in_response = next(
        (book for book in response.json() if book["id"] == str(test_book.id)), 
        None
    )
    
    # Assert that the test book is in the response and has the correct title
    assert test_book_in_response is not None
    assert test_book_in_response["title"] == test_book.title

def test_get_book(client, auth_headers, test_book):
    """Test getting a specific book"""
    response = client.get(f"/api/v1/books/{test_book.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == test_book.title

def test_get_nonexistent_book(client, auth_headers):
    """Test getting a book that doesn't exist"""
    response = client.get(f"/api/v1/books/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404

def test_create_book_as_author(client, auth_headers):
    """Test creating a book as an author"""
    book_data = {
        "title": "New Book",
        "content": "New Content"
    }
    response = client.post("/api/v1/books", headers=auth_headers, json=book_data)
    assert response.status_code == 200
    assert response.json()["title"] == book_data["title"]

def test_create_book_as_reader(client, reader_headers):
    """Test creating a book as a reader (should fail)"""
    book_data = {
        "title": "New Book",
        "content": "New Content"
    }
    response = client.post("/api/v1/books", headers=reader_headers, json=book_data)
    assert response.status_code == 403

def test_update_book(client, auth_headers, test_book):
    """Test updating a book"""
    update_data = {
        "title": "Updated Title",
        "content": "Updated Content"
    }
    response = client.put(
        f"/api/v1/books/{test_book.id}", 
        headers=auth_headers, 
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["title"] == update_data["title"]

def test_update_other_authors_book(client, reader_headers, test_book):
    """Test updating another author's book (should fail)"""
    update_data = {
        "title": "Updated Title",
        "content": "Updated Content"
    }
    response = client.put(
        f"/api/v1/books/{test_book.id}", 
        headers=reader_headers, 
        json=update_data
    )
    assert response.status_code == 403

def test_delete_book(client, auth_headers, test_book):
    """Test deleting a book"""
    response = client.delete(f"/api/v1/books/{test_book.id}", headers=auth_headers)
    assert response.status_code == 204

def test_delete_other_authors_book(client, reader_headers, test_book):
    """Test deleting another author's book (should fail)"""
    response = client.delete(f"/api/v1/books/{test_book.id}", headers=reader_headers)
    assert response.status_code == 403

def test_delete_nonexistent_book(client, auth_headers):
    """Test deleting a book that doesn't exist"""
    response = client.delete(f"/api/v1/books/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404
