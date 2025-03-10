from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from jose import JWTError, jwt
from uuid import UUID

from core.security import (
    create_access_token, 
    create_token_pair,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
)
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
    """Login to get access token and refresh token"""
    user = users.authenticate(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create both access and refresh tokens
    access_token, refresh_token = create_token_pair({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
def refresh_token(
    db: Session = Depends(get_session),
    refresh_token: str = Body(..., embed=True)
) -> dict:
    """Get a new access token using a refresh token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if it's a refresh token
        if payload.get("token_type") != "refresh":
            raise credentials_exception
        
        # Get the user ID from the token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Check if the user exists
        user = users.get(db, UUID(user_id))
        if user is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Create a new access token with a fresh expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
