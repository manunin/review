"""
API Routes for Smart Review Analyzer
"""

from fastapi import APIRouter
from app.api.endpoints import reviews, analytics, upload

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
