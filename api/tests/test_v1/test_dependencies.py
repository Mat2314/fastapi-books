import pytest
from uuid import uuid4
from fastapi import HTTPException
from jose import jwt

from v1.dependencies import get_current_user
from core.security import create_access_token, SECRET_KEY, ALGORITHM
from db.models import Users, AccountType


@pytest.fixture
def auth_test_user(db_session) -> Users:
    """Create a test user specifically for auth tests"""
    from db.crud.users import users
    
    email = "testauth@example.com"
    
    # Check if user already exists
    existing_user = users.get_by_email(db_session, email)
    if existing_user:
        return existing_user
    
    user_data = {
        "email": email,  # Different email from other tests
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "Auth",
        "account_type": AccountType.READER
    }
    return users.create(db_session, user_data)


@pytest.fixture
def valid_token(auth_test_user) -> str:
    """Create a valid JWT token for the test user"""
    return create_access_token({"sub": str(auth_test_user.id)})


@pytest.mark.asyncio
async def test_get_current_user_valid_token(
    db_session, auth_test_user, valid_token
):
    """Test successful user authentication with valid token"""
    user = await get_current_user(db_session, valid_token)
    assert user.id == auth_test_user.id
    assert user.email == auth_test_user.email


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session):
    """Test authentication failure with invalid token"""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db_session, "invalid_token")
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_expired_token(db_session, auth_test_user):
    """Test authentication failure with expired token"""
    # Create a token that's already expired
    import datetime
    from datetime import timedelta
    
    expired_time = datetime.datetime.now(datetime.UTC) - timedelta(minutes=30)
    
    to_encode = {"sub": str(auth_test_user.id), "exp": expired_time}
    expired_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db_session, expired_token)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_missing_sub_claim(db_session):
    """Test authentication failure with token missing sub claim"""
    # Create a token without the 'sub' claim
    token = jwt.encode({"not_sub": "something"}, SECRET_KEY, algorithm=ALGORITHM)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db_session, token)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user(db_session):
    """Test authentication failure with token for nonexistent user"""
    # Create a token with a random UUID that doesn't exist in the database
    nonexistent_id = str(uuid4())
    token = create_access_token({"sub": nonexistent_id})
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db_session, token)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_malformed_uuid(db_session):
    """Test authentication failure with token containing malformed UUID"""
    # Create a token with an invalid UUID format
    token = create_access_token({"sub": "not-a-uuid"})
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db_session, token)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials" 