"""
Review Analysis API - Main FastAPI Application

Implements the API specification from api/openapi.yml.
Task-based architecture for sentiment analysis.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.exceptions import (
    BaseAppException,
    ValidationError,
    app_exception_handler,
    general_exception_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging, get_logger
from app.core.security import (
    RequestTrackingMiddleware,
    SecurityHeadersMiddleware,
    setup_cors,
)
from app.infra.db.base import close_db, init_db
from app.tasks.router import router as task_router

# Configure logging first
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Review Analysis API", extra={"version": "1.0.0"})
    
    # Initialize database
    try:
        await init_db(settings.database_url)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # For now, continue without database for basic functionality
        # raise e  # Uncomment when database is required
    
    # TODO: Initialize other services here:
    # app.state.redis = await create_redis_pool(settings.redis_url)
    # app.state.ml_model = await load_ml_model()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Smart Review Analyzer API")
    
    # Cleanup database connections
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
    
    # TODO: Cleanup resources here:
    # await app.state.db_engine.dispose()
    # await app.state.redis.close()
    # await app.state.ml_model.cleanup()


# Initialize FastAPI app
app = FastAPI(
    title="Review Analysis API",
    description="""Task-based API for review analysis with support for sentiment analysis.

The system works with a task-based architecture:
- Submit analysis tasks (single text or batch file)
- Retrieve results of completed tasks
- All operations use POST method for consistency
- User identification via cookies""",
    version="1.0.0",
    contact={
        "name": "Review Analysis System",
        "url": "https://github.com/manunin/review",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    servers=[
        {
            "url": "/api/v1",
            "description": "Development server"
        }
    ],
    lifespan=lifespan,
)

# Setup CORS using our security module
setup_cors(app)

# Add middleware (order matters!)
app.add_middleware(RequestTrackingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Register exception handlers
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API routes according to OpenAPI specification
app.include_router(task_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Review Analysis API",
        "version": "1.0.0",
        "docs": "/api/v1/docs",
        "openapi": "/api/v1/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None,  # Use our custom logging
    )
