from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from db.crud.users import users
from db.database import get_session
from db.models import Users, AccountType

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(
    *,
    db: Session = Depends(get_session),
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    account_type: AccountType
) -> Users:
    """Register a new user"""
    # Check if user exists
    if users.get_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    user_in = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "account_type": account_type
    }
    user = users.create(db, user_in)
    return user


@router.post("/login")
def login(
    db: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> dict:
    """Login to get access token"""
    print("\nLogin attempt:", {
        "username": form_data.username,
        "password": form_data.password,  # Don't log passwords in production!
    })
    print(f"#########################")
    print(f"Users in db auth: {db.exec(select(Users)).all()}")
    print(f"#########################")
    user = users.authenticate(db, form_data.username, form_data.password)
    print("User found:", user is not None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
