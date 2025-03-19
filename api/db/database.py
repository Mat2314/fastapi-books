from sqlmodel import create_engine, SQLModel, Session
from core.config import settings
import os
import logging
import time

# Import models - keep the import * for model registration with SQLModel
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
        
        # First try direct connection via private IP if available
        if settings.POSTGRES_HOST and settings.POSTGRES_HOST != "localhost":
            logger.info(f"Using direct connection to Cloud SQL via private IP: {settings.POSTGRES_HOST}")
            return (
                f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
                f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
            )
        # Fall back to Unix socket if private IP is not available
        elif settings.CLOUD_SQL_CONNECTION_NAME:
            logger.info(f"Cloud SQL connection name: {settings.CLOUD_SQL_CONNECTION_NAME}")
            # Format for Cloud SQL with Unix socket
            socket_path = f"/cloudsql/{settings.CLOUD_SQL_CONNECTION_NAME}/.s.PGSQL.5432"
            logger.info(f"Socket path: {socket_path}")
            
            # Check if socket file exists
            if os.path.exists(f"/cloudsql/{settings.CLOUD_SQL_CONNECTION_NAME}"):
                logger.info("Socket directory exists")
            else:
                logger.warning(f"Socket directory does not exist: /cloudsql/{settings.CLOUD_SQL_CONNECTION_NAME}")
            
            # Use pg8000 for Cloud SQL
            db_url = (
                f"postgresql+pg8000://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
                f"@/{settings.POSTGRES_DB}?unix_sock={socket_path}"
            )
            logger.info(f"Using Cloud SQL connection URL: {db_url}")
            return db_url
        else:
            # Fallback to TCP connection if no socket available
            logger.warning("No Cloud SQL connection method available, using default TCP connection")
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
        
        # Create engine with connection pooling and retry logic
        connect_args = {}
        
        # Add appropriate timeout parameter based on the driver
        if "+pg8000" in db_url:
            # pg8000 uses timeout in seconds
            connect_args["timeout"] = 30
        else:
            # psycopg2 uses connect_timeout in seconds
            connect_args["connect_timeout"] = 30
        
        engine = create_engine(
            db_url, 
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,  # Recycle connections every 5 minutes
            connect_args=connect_args
        )
    return engine


def init_db():
    """Initialize database schema"""
    try:
        # In production, don't auto-create schema - rely on migrations only
        if settings.ENVIRONMENT == "production":
            logger.info("Running in production mode - skipping automatic schema creation")
            logger.info("Database schema should be managed by Alembic migrations only")
            return
            
        # Only run automatic schema creation in development/testing
        logger.info("Initializing database schema in development mode")
        
        # Add retry logic for database initialization
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                SQLModel.metadata.create_all(get_engine())
                logger.info("Database schema initialized successfully")
                return
            except Exception as e:
                # Check if it's a "DuplicateObject" error, which is okay to ignore
                if "DuplicateObject" in str(e) and "already exists" in str(e):
                    logger.info(f"Ignoring duplicate object error: {e}")
                    return
                    
                if attempt < max_retries - 1:
                    logger.warning(f"Database initialization attempt {attempt+1} failed: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise
                    
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
