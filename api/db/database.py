from functools import lru_cache
from sqlmodel import create_engine, SQLModel, Session
from core.config import settings
import os
import logging

from db.models import *

logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """Get database URL based on environment"""
    if os.getenv("TESTING"):
        # Testing database
        logger.info("Using testing database")
        return (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/test_db"
        )
    
    # Check if we're in production environment
    if settings.ENVIRONMENT == "production":
        logger.info("Using Cloud SQL in production environment")
        
        # Check if we have a Cloud SQL connection name
        if settings.CLOUD_SQL_CONNECTION_NAME:
            # Format for Cloud SQL with Unix socket
            # postgresql+pg8000://<db_user>:<db_pass>@/<db_name>?unix_sock=/cloudsql/<cloud_sql_instance_name>/.s.PGSQL.5432
            return (
                f"postgresql+pg8000://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
                f"@/{settings.POSTGRES_DB}?unix_sock=/cloudsql/{settings.CLOUD_SQL_CONNECTION_NAME}/.s.PGSQL.5432"
            )
        else:
            # Fallback to TCP connection if no socket available
            logger.warning("No Cloud SQL connection name provided, using TCP connection")
            return (
                f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
                f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
            )
    
    # Development database (local)
    logger.info("Using local development database")
    return (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

# Create engine based on environment
engine = None

def get_engine():
    """Get or create SQLAlchemy engine with lazy initialization"""
    global engine
    if engine is None:
        db_url = get_database_url()
        logger.info(f"Initializing database connection to: {db_url}")
        engine = create_engine(db_url, echo=False, pool_pre_ping=True)
    return engine

def init_db():
    """Initialize database schema"""
    try:
        logger.info("Initializing database schema")
        SQLModel.metadata.create_all(get_engine())
        logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        if settings.ENVIRONMENT != "production":
            # In development, we want to fail if DB init fails
            raise
        # In production, we'll continue even if DB init fails
        # This allows the API to start and serve non-DB endpoints

def get_session():
    """Get database session"""
    with Session(get_engine()) as session:
        yield session
