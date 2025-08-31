"""
Smart Review Analyzer - Main FastAPI Application

This is the main entry point for the Smart Review Analyzer API.
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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

# Configure logging first
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Smart Review Analyzer API", extra={"version": "1.0.0"})
    
    # TODO: Initialize services here:
    # engine, session_factory = await create_engine_session(settings.database_url)
    # app.state.db_engine = engine  
    # app.state.db_session_factory = session_factory
    # app.state.redis = await create_redis_pool(settings.redis_url)
    # app.state.ml_model = await load_ml_model()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Smart Review Analyzer API")
    
    # TODO: Cleanup resources here:
    # await app.state.db_engine.dispose()
    # await app.state.redis.close()
    # await app.state.ml_model.cleanup()


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered review analysis platform for sentiment detection",
    version="1.0.0",  # TODO: get from settings.version when available
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
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

# Include API routes (placeholder for now)
# from app.api.routes import api_router
# app.include_router(api_router, prefix="/api/v1")

# Mount static files (for file uploads, model files, etc.)
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint providing API information."""
    return {
        "message": "Welcome to Smart Review Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/healthz")
async def health_check_basic() -> dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0",
    }


@app.get("/readyz") 
async def health_check_ready() -> dict[str, Any]:
    """Readiness check endpoint (DB, Redis, ML model)."""
    # TODO: Add actual health checks for:
    # - Database connection
    # - Redis connection
    # - ML model availability
    return {
        "status": "ready",
        "service": settings.app_name,
        "version": "1.0.0",
        "environment": settings.environment,
        "checks": {
            "database": "ok",  # TODO: implement actual check
            "redis": "ok",     # TODO: implement actual check  
            "ml_model": "ok"   # TODO: implement actual check
        }
    }


@app.get("/api/v1/health")
async def health_check() -> dict[str, Any]:
    """Legacy health check endpoint."""
    return {
        "status": "healthy", 
        "service": settings.app_name,
        "version": "1.0.0",
        "environment": settings.environment,
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
