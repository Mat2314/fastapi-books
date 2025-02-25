import pytest
from sqlmodel import Session
from db.crud.users import CRUDUser
from db.models import Users, AccountType

@pytest.fixture
def crud_user():
    return CRUDUser(Users)

@pytest.fixture
def sample_user():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "secret",
        "account_type": AccountType.READER
    }

def test_get_user_by_email(crud_user, db_session: Session, sample_user):
    # Create a user first
    user = Users(**sample_user)
    db_session.add(user)
    db_session.commit()

    # Test getting user by email
    found_user = crud_user.get_by_email(db_session, email=sample_user["email"])
    assert found_user is not None
    assert found_user.email == sample_user["email"]

def test_get_user_by_email_not_found(crud_user, db_session: Session):
    found_user = crud_user.get_by_email(db_session, email="nonexistent@example.com")
    assert found_user is None
