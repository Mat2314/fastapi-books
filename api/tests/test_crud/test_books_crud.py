import pytest
from uuid import uuid4
from sqlmodel import Session
from db.crud.books import CRUDBooks
from db.crud.users import users
from db.models import Books, Users, AccountType

@pytest.fixture
def crud_books():
    return CRUDBooks(Books)

@pytest.fixture
def test_author(db_session: Session) -> Users:
    """Create a test author"""
    author_data = {
        "email": "author@test.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "Author",
        "account_type": AccountType.AUTHOR
    }
    return users.create(db_session, author_data)

@pytest.fixture
def sample_book(test_author: Users):
    return {
        "id": uuid4(),
        "title": "Sample Book",
        "author_id": test_author.id,  # Use the actual author ID
        "description": "A test book",
        "content": "This is the book content"
    }

def test_get_user_books(db_session: Session, crud_books: CRUDBooks, test_author: Users):
    # Create multiple books for different authors
    other_author = users.create(db_session, {
        "email": "other@test.com",
        "password": "password123",
        "first_name": "Other",
        "last_name": "Author",
        "account_type": AccountType.AUTHOR
    })
    
    # Create books for our target author
    books_author1 = [
        {
            "id": uuid4(),
            "title": f"Book {i}",
            "author_id": test_author.id,
            "description": "A test book",
            "content": "This is the book content"
        }
        for i in range(3)
    ]
    for book in books_author1:
        crud_books.create(db_session, book)
    
    # Create a book for different author
    other_book = {
        "id": uuid4(),
        "title": "Other Book",
        "author_id": other_author.id,
        "description": "A test book",
        "content": "This is the book content"
    }
    crud_books.create(db_session, other_book)

    # Test basic retrieval
    result = crud_books.get_books_by_author(db_session, test_author.id)
    assert len(result) == 3
    assert all(book.author_id == test_author.id for book in result)

    # Test pagination with skip
    result = crud_books.get_books_by_author(db_session, test_author.id)
    assert len(result) == 3

    # Test pagination with limit
    result = crud_books.get_books_by_author(db_session, test_author.id)
    assert len(result) == 3

    # Test with non-existent author
    non_existent_id = uuid4()
    result = crud_books.get_books_by_author(db_session, non_existent_id)
    assert len(result) == 0 