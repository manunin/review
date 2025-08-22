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
        "statistics": stats,
        "insights": {
            "dominant_sentiment": max(
                [("positive", stats["positive"]), ("negative", stats["negative"]), ("neutral", stats["neutral"])],
                key=lambda x: x[1]
            )[0] if stats["total_reviews"] > 0 else "none",
            "sentiment_distribution": {
                "positive": stats["positive_percentage"],
                "negative": stats["negative_percentage"],
                "neutral": stats["neutral_percentage"]
            }
        }
    }


@router.get("/sentiment/{sentiment}")
async def get_sentiment_breakdown(
    sentiment: str,
    db: Session = Depends(get_db)
):
    """Get detailed breakdown for a specific sentiment."""
    if sentiment not in ["positive", "negative", "neutral"]:
        raise HTTPException(status_code=400, detail="Invalid sentiment. Must be 'positive', 'negative', or 'neutral'")
    
    review_service = ReviewService(db)
    reviews = review_service.get_reviews_by_sentiment(sentiment)
    
    return {
        "sentiment": sentiment,
        "count": len(reviews),
        "reviews": [
            {
                "id": review.id,
                "text": review.text[:100] + "..." if len(review.text) > 100 else review.text,
                "confidence": review.confidence,
                "created_at": review.created_at
            }
            for review in reviews
        ]
    }
