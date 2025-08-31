"""
Analytics endpoints for sentiment statistics
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.review_service import ReviewService

router = APIRouter()


@router.get("/summary")
async def get_analytics_summary(db: Session = Depends(get_db)):
    """Get overall sentiment analytics summary."""
    review_service = ReviewService(db)
    stats = review_service.get_sentiment_statistics()
    
    return {
        "statistics": stats
    }
