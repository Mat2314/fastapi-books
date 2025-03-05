import pytest
from uuid import uuid4
from sqlmodel import Session

from db.crud.users import CRUDUsers
from db.models import Users, AccountType
from core.security import verify_password


# Counter for generating unique emails
_email_counter = 0


@pytest.fixture
def crud_users():
    return CRUDUsers(Users)


@pytest.fixture
def sample_user():
    """Generate a unique user for each test"""
    global _email_counter
    _email_counter += 1
    email = f"test_{_email_counter}@example.com"
    return {
        "email": email,
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "account_type": AccountType.READER
    }


def test_create_user(
    db_session: Session, crud_users: CRUDUsers, sample_user: dict
):
    # Test creating a user
    user = crud_users.create(db_session, sample_user)
    
    assert user.email == sample_user["email"]
    assert user.first_name == sample_user["first_name"]
    assert user.last_name == sample_user["last_name"]
    assert user.account_type == sample_user["account_type"]
    # Verify password was hashed
    assert verify_password(sample_user["password"], user.password)
    assert user.id is not None


def test_authenticate_user(
    db_session: Session, crud_users: CRUDUsers, sample_user: dict
):
    # Create test user
    crud_users.create(db_session, sample_user)
    
    # Test successful authentication
    authenticated_user = crud_users.authenticate(
        db_session,
        email=sample_user["email"],
        password=sample_user["password"]
    )
    assert authenticated_user is not None
    assert authenticated_user.email == sample_user["email"]
    
    # Test failed authentication cases
    assert crud_users.authenticate(
        db_session,
        email=sample_user["email"],
        password="wrongpassword"
    ) is None
    
    assert crud_users.authenticate(
        db_session,
        email="wrong@email.com",
        password=sample_user["password"]
    ) is None


def test_get_by_email(
    db_session: Session, crud_users: CRUDUsers, sample_user: dict
):
    # Create test user
    created_user = crud_users.create(db_session, sample_user)
    
    # Test getting existing user
    found_user = crud_users.get_by_email(db_session, sample_user["email"])
    assert found_user is not None
    assert found_user.id == created_user.id
    
    # Test getting non-existent user
    not_found = crud_users.get_by_email(db_session, "nonexistent@example.com")
    assert not_found is None


def test_get_user(
    db_session: Session, crud_users: CRUDUsers, test_user: Users
):
    # Test getting existing user
    found_user = crud_users.get(db_session, test_user.id)
    assert found_user is not None
    assert found_user.id == test_user.id
    
    # Test getting non-existent user
    not_found = crud_users.get(db_session, uuid4())
    assert not_found is None


def test_update_user(
    db_session: Session, crud_users: CRUDUsers, sample_user: dict
):
    # Create test user
    created_user = crud_users.create(db_session, sample_user)
    
    # Update user
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    updated_user = crud_users.update(db_session, created_user.id, update_data)
    
    assert updated_user is not None
    assert updated_user.id == created_user.id
    assert updated_user.first_name == update_data["first_name"]
    assert updated_user.last_name == update_data["last_name"]
    assert updated_user.email == sample_user["email"]  # Unchanged field


def test_delete_user(
    db_session: Session, crud_users: CRUDUsers, sample_user: dict
):
    # Create test user
    created_user = crud_users.create(db_session, sample_user)
    
    # Test successful deletion
    assert crud_users.delete(db_session, created_user.id) is True
    assert crud_users.get(db_session, created_user.id) is None
    
    # Test deleting non-existent user
    assert crud_users.delete(db_session, uuid4()) is False


def test_get_multi_users(db_session: Session, crud_users: CRUDUsers):
    # Create multiple test users
    users_data = [
        {
            "email": f"user{i}@example.com",
            "password": f"password{i}",
            "first_name": f"User{i}",
            "last_name": "Test",
            "account_type": AccountType.READER
        }
        for i in range(3)
    ]
    
    for user_data in users_data:
        crud_users.create(db_session, user_data)
    
    # Test pagination
    all_users = crud_users.get_multi(db_session)
    assert len(all_users) >= 3
    
    limited_users = crud_users.get_multi(db_session, limit=2)
    assert len(limited_users) == 2
    
    skipped_users = crud_users.get_multi(db_session, skip=1, limit=2)
    assert len(skipped_users) == 2
    assert skipped_users[0] != all_users[0]


def test_create_user_with_none_values(
    db_session: Session, crud_users: CRUDUsers
):
    # Test creating a user with minimal required fields
    user_data = {
        "email": "minimal@example.com",
        "password": "pass123",
        "first_name": "Min",
        "last_name": "User"
        # account_type will default to READER
    }
    user = crud_users.create(db_session, user_data)
    assert user.account_type == AccountType.READER


def test_authenticate_user_detailed(
    db_session: Session, crud_users: CRUDUsers, sample_user: dict
):
    # Create test user
    created_user = crud_users.create(db_session, sample_user)
    
    # Test each authentication failure case separately
    # Test non-existent user
    result = crud_users.authenticate(
        db_session,
        email="nonexistent@example.com",
        password=sample_user["password"]
    )
    assert result is None

    # Test wrong password
    result = crud_users.authenticate(
        db_session,
        email=sample_user["email"],
        password="wrongpass"
    )
    assert result is None

    # Test successful case
    result = crud_users.authenticate(
        db_session,
        email=sample_user["email"],
        password=sample_user["password"]
    )
    assert result is not None
    assert result.id == created_user.id


def test_get_by_email_detailed(
    db_session: Session, crud_users: CRUDUsers, sample_user: dict
):
    # Create test user
    created_user = crud_users.create(db_session, sample_user)
    
    # Test exact email match
    found_user = crud_users.get_by_email(db_session, sample_user["email"])
    assert found_user is not None
    assert found_user.id == created_user.id
    
    # Test case sensitivity
    found_user = crud_users.get_by_email(
        db_session, sample_user["email"].upper()
    )
    assert found_user is None  # Should be None as emails are case-sensitive
    
    # Test non-existent email
    not_found = crud_users.get_by_email(
        db_session, "nonexistent@example.com"
    )
    assert not_found is None 