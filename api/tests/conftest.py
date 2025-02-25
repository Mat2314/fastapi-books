import pytest
from sqlmodel import Session, create_engine
from db.models import Users

@pytest.fixture(name="engine")
def engine_fixture():
    # Create SQLite in-memory database for testing
    engine = create_engine("sqlite:///", echo=False)
    # Create all tables
    Users.metadata.create_all(engine)
    yield engine
    # Drop all tables after tests
    Users.metadata.drop_all(engine)

@pytest.fixture(name="db_session")
def db_session_fixture(engine):
    with Session(engine) as session:
        yield session 
