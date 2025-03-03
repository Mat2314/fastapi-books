import pytest
from uuid import uuid4
from fastapi import HTTPException
from jose import jwt

from v1.dependencies import get_current_user
from core.security import create_access_token, SECRET_KEY, ALGORITHM
from db.models import Users, AccountType


@pytest.fixture
def test_user(db_session) -> Users:
    """Create a test user and return it"""
    from db.crud.users import users
    user_data = {
        "email": "testauth@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "Auth",
        "account_type": AccountType.READER
    }
    return users.create(db_session, user_data)


@pytest.fixture
def valid_token(test_user) -> str:
    """Create a valid JWT token for the test user"""
    return create_access_token({"sub": str(test_user.id)})


async def test_get_current_user_valid_token(db_session, test_user, valid_token):
    """Test successful user authentication with valid token"""
    user = await get_current_user(db_session, valid_token)
    assert user.id == test_user.id
    assert user.email == test_user.email


async def test_get_current_user_invalid_token(db_session):
    """Test authentication failure with invalid token"""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db_session, "invalid_token")
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


async def test_get_current_user_expired_token(db_session, test_user):
    """Test authentication failure with expired token"""
    # Create an expired token by manually encoding with expired timestamp
    from datetime import datetime, timedelta
    expired_timestamp = datetime.now(datetime.UTC) - timedelta(days=1)
    
    expired_token = jwt.encode(
        {"sub": str(test_user.id), "exp": expired_timestamp},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db_session, expired_token)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


async def test_get_current_user_missing_sub_claim(db_session):
    """Test authentication failure with token missing sub claim"""
    token = jwt.encode(
        {"some_other_claim": "value"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db_session, token)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


async def test_get_current_user_nonexistent_user(db_session):
    """Test authentication failure with token for non-existent user"""
    # Create token with non-existent user ID
    token = create_access_token({"sub": str(uuid4())})
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db_session, token)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


async def test_get_current_user_malformed_uuid(db_session):
    """Test authentication failure with malformed UUID in token"""
    token = create_access_token({"sub": "not-a-uuid"})
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db_session, token)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials" 