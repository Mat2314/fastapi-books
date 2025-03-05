from functools import lru_cache
from sqlmodel import create_engine, SQLModel, Session
from core.config import settings
import os

from db.models import *

def get_database_url() -> str:
    """Get database URL based on environment"""
    if os.getenv("TESTING"):
        # Testing database
        return (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/test_db"
        )
    # Development/Production database
    return (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

# Create engine based on environment
engine = create_engine(get_database_url(), echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
