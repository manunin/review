"""
Smart Review Analyzer - Main FastAPI Application

This is the main entry point for the Smart Review Analyzer API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.core.config import settings
from app.api.routes import api_router

# Initialize FastAPI app
app = FastAPI(
    title="Smart Review Analyzer API",
    description="AI-powered review analysis platform for sentiment detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount static files (for file uploads, model files, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Welcome to Smart Review Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Smart Review Analyzer API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
