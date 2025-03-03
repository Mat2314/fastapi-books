import pytest
from uuid import uuid4
from sqlmodel import Session
from db.crud.books import CRUDBooks
from db.models import Books

@pytest.fixture
def crud_books():
    return CRUDBooks(Books)

@pytest.fixture
def sample_book():
    return {
        "id": uuid4(),
        "title": "Sample Book",
        "author_id": uuid4(),
        "description": "A test book",
        "content": "This is the book content"
    }

def test_get_user_books(db_session: Session, crud_books: CRUDBooks, sample_book: dict):
    # Create multiple books for different authors
    author_id = uuid4()
    other_author_id = uuid4()
    
    # Create books for our target author
    books_author1 = [
        {**sample_book, "id": uuid4(), "title": f"Book {i}", "author_id": author_id}
        for i in range(3)
    ]
    for book in books_author1:
        crud_books.create(db_session, book)
    
    # Create a book for different author
    other_book = {**sample_book, "id": uuid4(), "author_id": other_author_id}
    crud_books.create(db_session, other_book)

    # Test basic retrieval
    result = crud_books.get_books_by_author(db_session, author_id)
    assert len(result) == 3
    assert all(book.author_id == author_id for book in result)

    # Test pagination with skip
    result = crud_books.get_books_by_author(db_session, author_id)
    assert len(result) == 3

    # Test pagination with limit
    result = crud_books.get_books_by_author(db_session, author_id)
    assert len(result) == 3

    # Test with non-existent author
    non_existent_id = uuid4()
    result = crud_books.get_books_by_author(db_session, non_existent_id)
    assert len(result) == 0 