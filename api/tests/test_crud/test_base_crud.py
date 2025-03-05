import pytest
from uuid import UUID, uuid4
from sqlmodel import Session
from db.crud.base import CRUDBase
from db.models import Users, AccountType

@pytest.fixture
def crud_base():
    return CRUDBase(Users)

@pytest.fixture
def sample_user():
    return {
        "id": uuid4(),
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "secret",
        "account_type": AccountType.READER
    }

def test_create(db_session: Session, crud_base: CRUDBase, sample_user: dict):
    # Test create method
    user = crud_base.create(db_session, sample_user)
    assert user.first_name == sample_user["first_name"]
    assert user.email == sample_user["email"]

def test_get(db_session: Session, crud_base: CRUDBase, test_user: Users):
    # Test get method using existing user
    retrieved_user = crud_base.get(db_session, test_user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == test_user.id
    assert retrieved_user.email == test_user.email

def test_get_non_existent(db_session: Session, crud_base: CRUDBase):
    # Test getting non-existent user
    non_existent = crud_base.get(db_session, uuid4())
    assert non_existent is None

def test_get_multi(db_session: Session, crud_base: CRUDBase, test_user: Users):
    # Test get_multi method using existing user
    users = crud_base.get_multi(db_session)
    assert len(users) > 0
    assert test_user in users

def test_update(db_session: Session, crud_base: CRUDBase, test_user: Users):
    # Test update method
    update_data = {"first_name": "Updated"}
    updated_user = crud_base.update(db_session, test_user.id, update_data)
    assert updated_user.first_name == "Updated"

def test_update_non_existent(db_session: Session, crud_base: CRUDBase):
    # Test updating non-existent user
    updated = crud_base.update(db_session, uuid4(), {"first_name": "Jane"})
    assert updated is None

def test_delete(db_session: Session, crud_base: CRUDBase, test_user: Users):
    # Create a new user for delete test
    new_user_data = {
        "email": "delete_test@example.com",  # Different email
        "password": "testpass123",
        "first_name": "Delete",
        "last_name": "Test",
        "account_type": AccountType.READER
    }
    user_to_delete = crud_base.create(db_session, new_user_data)
    
    # Test delete method
    assert crud_base.delete(db_session, user_to_delete.id) is True
    assert crud_base.get(db_session, user_to_delete.id) is None 