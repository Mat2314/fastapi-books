from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from db.crud.users import users
from db.database import get_session
from db.models import Users
from v1.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/all", response_model=List[Users])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    _: Users = Depends(get_current_user),
):
    """Get all users"""
    all_users = users.get_multi(db, skip=skip, limit=limit)
    return all_users


@router.get("/{user_id}", response_model=Users)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_session),
    _: Users = Depends(get_current_user),
):
    """Get a specific user and their books (if they are an author)"""
    user = users.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Books will be included in the response due to the relationship 
    # (if user is an author)
    return user
