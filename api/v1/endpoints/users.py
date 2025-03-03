from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from db.crud.users import users
from db.crud.books import books
from db.database import get_session
from db.models import Users, Books, AccountType
from v1.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/authors", response_model=List[Users])
def get_authors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    _: Users = Depends(get_current_user),
):
    """Get all authors"""
    authors = users.get_multi(db, skip=skip, limit=limit)
    return authors


@router.get("/authors/{author_id}", response_model=Users)
def get_author(
    author_id: UUID,
    db: Session = Depends(get_session),
    _: Users = Depends(get_current_user),
):
    """Get a specific author and their books"""
    author = users.get(db, author_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )
    if author.account_type != AccountType.AUTHOR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an author",
        )
    
    # Books will be included in the response due to the relationship
    return author
