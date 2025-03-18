from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import init_db
from v1.endpoints import books, auth, users
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles database initialization and cleanup.
    """
    try:
        logger.info(f"Starting application in {os.getenv('ENVIRONMENT', 'development')} mode")
        # Initialize database
        init_db()
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # In production, we'll continue even if there's an error
        # This allows the API to start and serve non-DB endpoints
    
    yield
    
    # Cleanup code (if needed)
    logger.info("Shutting down application")


app = FastAPI(
    title="FastAPI Books API",
    description="API for managing books",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "http://localhost:4200",  # Angular app
    "http://127.0.0.1:4200",
    # Add your Cloud Run URLs here
    "https://fabooks-service-254943040140.us-central1.run.app",
    "https://fabooks-frontend-254943040140.us-central1.run.app",  # Frontend Cloud Run URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(books.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint for health checks"""
    return {
        "message": "FastAPI Books API",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "development")
    }
