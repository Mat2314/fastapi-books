from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from db.crud.books import books
from db.database import get_session
from db.models import Books, Users, AccountType
from v1.dependencies import get_current_user

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=List[Books])
def get_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    _: Users = Depends(get_current_user),
):
    """Get all books"""
    return books.get_multi(db, skip=skip, limit=limit)


@router.get("/{book_id}", response_model=Books)
def get_book(
    book_id: UUID,
    db: Session = Depends(get_session),
    _: Users = Depends(get_current_user),
):
    """Get a specific book by ID"""
    db_book = books.get(db, book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return db_book


@router.post("", response_model=Books)
def create_book(
    *,
    db: Session = Depends(get_session),
    book_in: dict,
    current_user: Users = Depends(get_current_user),
):
    """Create a new book (authors only)"""
    if current_user.account_type != AccountType.AUTHOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authors can create books",
        )
    return books.create_book(db, book_in, current_user)


@router.put("/{book_id}", response_model=Books)
def update_book(
    *,
    db: Session = Depends(get_session),
    book_id: UUID,
    book_in: dict,
    current_user: Users = Depends(get_current_user),
):
    """Update a book (author of the book only)"""
    db_book = books.get(db, book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    if db_book.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author can modify this book",
        )
    return books.update(db, book_id, book_in)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    *,
    db: Session = Depends(get_session),
    book_id: UUID,
    current_user: Users = Depends(get_current_user),
):
    """Delete a book (author of the book only)"""
    db_book = books.get(db, book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    if db_book.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author can delete this book",
        )
    books.delete(db, book_id) 