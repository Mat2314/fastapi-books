import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
import time

from db.models import Users, AccountType
from db.crud.users import users


@pytest.fixture
def test_user(db_session: Session) -> Users:
    """Create a test user"""
    email = "test_auth@example.com"
    
    # Check if user already exists
    existing_user = users.get_by_email(db_session, email)
    if existing_user:
        return existing_user
    
    user_data = {
        "email": email,
        "password": "password123",
        "first_name": "Test",
        "last_name": "Auth",
        "account_type": AccountType.READER
    }
    
    return users.create(db_session, user_data)


def test_login(client: TestClient, test_user: Users):
    """Test login endpoint"""
    response = client.post(
        "/api/v1/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": test_user.email,
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token(client: TestClient, test_user: Users):
    """Test refresh token endpoint"""
    # First, get a refresh token by logging in
    login_response = client.post(
        "/api/v1/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": test_user.email,
            "password": "password123"
        }
    )
    
    assert login_response.status_code == 200
    login_data = login_response.json()
    refresh_token = login_data["refresh_token"]
    
    # Add a small delay to ensure different token generation times
    time.sleep(1)
    
    # Now use the refresh token to get a new access token
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data
    assert refresh_data["token_type"] == "bearer"
    
    # Verify the new access token is different from the old one
    assert refresh_data["access_token"] != login_data["access_token"]


def test_refresh_token_invalid(client: TestClient):
    """Test refresh token endpoint with invalid token"""
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"}
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_refresh_token_with_access_token(client: TestClient, test_user: Users):
    """Test refresh token endpoint with access token
    
    Tests using an access token instead of a refresh token
    """
    # First, get an access token by logging in
    login_response = client.post(
        "/api/v1/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": test_user.email,
            "password": "password123"
        }
    )
    
    assert login_response.status_code == 200
    login_data = login_response.json()
    access_token = login_data["access_token"]
    
    # Try to use the access token as a refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token}
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials" 