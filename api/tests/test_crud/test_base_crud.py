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

def test_get(db_session: Session, crud_base: CRUDBase, sample_user: dict):
    # Create a user first
    user = crud_base.create(db_session, sample_user)
    # Test get method
    retrieved_user = crud_base.get(db_session, user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.email == user.email

def test_get_non_existent(db_session: Session, crud_base: CRUDBase):
    # Test getting non-existent user
    non_existent = crud_base.get(db_session, uuid4())
    assert non_existent is None

def test_get_multi(db_session: Session, crud_base: CRUDBase, sample_user: dict):
    # Create multiple users
    user1 = crud_base.create(db_session, sample_user)
    user2 = crud_base.create(db_session, {**sample_user, "id": uuid4(), "email": "jane@example.com"})
    
    # Test get_multi method
    users = crud_base.get_multi(db_session, skip=0, limit=10)
    assert len(users) == 2
    assert any(u.id == user1.id for u in users)
    assert any(u.id == user2.id for u in users)

    # Test pagination
    users = crud_base.get_multi(db_session, skip=1, limit=1)
    assert len(users) == 1

def test_update(db_session: Session, crud_base: CRUDBase, sample_user: dict):
    # Create a user first
    user = crud_base.create(db_session, sample_user)
    
    # Test update method
    updated_data = {"first_name": "Jane", "email": "jane@example.com"}
    updated_user = crud_base.update(db_session, user.id, updated_data)
    
    assert updated_user is not None
    assert updated_user.first_name == "Jane"
    assert updated_user.email == "jane@example.com"
    assert updated_user.last_name == user.last_name  # Unchanged field

def test_update_non_existent(db_session: Session, crud_base: CRUDBase):
    # Test updating non-existent user
    updated = crud_base.update(db_session, uuid4(), {"first_name": "Jane"})
    assert updated is None

def test_delete(db_session: Session, crud_base: CRUDBase, sample_user: dict):
    # Create a user first
    user = crud_base.create(db_session, sample_user)
    
    # Test delete method
    result = crud_base.delete(db_session, user.id)
    assert result is True
    
    # Verify user is deleted
    assert crud_base.get(db_session, user.id) is None

def test_delete_non_existent(db_session: Session, crud_base: CRUDBase):
    # Test deleting non-existent user
    result = crud_base.delete(db_session, uuid4())
    assert result is False 