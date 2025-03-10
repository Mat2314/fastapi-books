import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlmodel import Session

from db.crud.books import books
from db.crud.users import users
from db.models import AccountType, Users

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
def test_book(db_session: Session, test_author: Users):
    """Create a test book"""
    book_data = {
        "title": "Test Book",
        "content": "This is the content of the test book.",
        "author_id": test_author.id
    }
    
    return books.create(db_session, book_data)

def test_get_books(client: TestClient, auth_headers, test_book):
    """Test getting all books"""
    response = client.get("/api/v1/books", headers=auth_headers)
    assert response.status_code == 200
    
    # Check that at least one book is returned
    books_list = response.json()
    assert len(books_list) > 0
    
    # Find the test book in the response by ID
    test_book_in_response = next(
        (book for book in books_list if book["id"] == str(test_book.id)),
        None
    )
    
    # Assert that the test book is in the response
    assert test_book_in_response is not None
    assert test_book_in_response["title"] == test_book.title

def test_get_book(client: TestClient, auth_headers, test_book):
    """Test getting a specific book"""
    response = client.get(f"/api/v1/books/{test_book.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == test_book.title

def test_get_nonexistent_book(client: TestClient, auth_headers):
    """Test getting a book that doesn't exist"""
    response = client.get(f"/api/v1/books/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404

def test_create_book_as_author(client: TestClient, auth_headers):
    """Test creating a book as an author"""
    book_data = {
        "title": "New Test Book",
        "content": "This is the content of the new test book."
    }
    
    response = client.post("/api/v1/books", json=book_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == book_data["title"]

def test_create_book_as_reader(client: TestClient, reader_headers):
    """Test creating a book as a reader (should fail)"""
    book_data = {
        "title": "Reader's Book",
        "content": "This is a book that shouldn't be created"
    }
    
    response = client.post("/api/v1/books", json=book_data, headers=reader_headers)
    assert response.status_code == 403

def test_update_book(client: TestClient, auth_headers, test_book):
    """Test updating a book"""
    update_data = {
        "title": "Updated Test Book",
        "content": "Updated content"
    }
    
    response = client.put(
        f"/api/v1/books/{test_book.id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == update_data["title"]

def test_update_other_authors_book(client: TestClient, reader_headers, test_book):
    """Test updating another author's book (should fail)"""
    update_data = {
        "title": "Reader's Update",
        "description": "This update should fail"
    }
    
    response = client.put(
        f"/api/v1/books/{test_book.id}",
        json=update_data,
        headers=reader_headers
    )
    assert response.status_code == 403

def test_delete_book(client: TestClient, auth_headers, test_book):
    """Test deleting a book"""
    response = client.delete(f"/api/v1/books/{test_book.id}", headers=auth_headers)
    assert response.status_code == 204

def test_delete_other_authors_book(client: TestClient, reader_headers, test_book):
    """Test deleting another author's book (should fail)"""
    response = client.delete(f"/api/v1/books/{test_book.id}", headers=reader_headers)
    assert response.status_code == 403

def test_delete_nonexistent_book(client: TestClient, auth_headers):
    """Test deleting a book that doesn't exist"""
    response = client.delete(f"/api/v1/books/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404
