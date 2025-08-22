"""
Review analysis endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewAnalyzeRequest
from app.services.review_service import ReviewService
from app.services.ml_service import MLService

router = APIRouter()


@router.post("/analyze", response_model=ReviewResponse)
async def analyze_single_review(
    request: ReviewAnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze sentiment of a single review text.
    """
    try:
        ml_service = MLService()
        review_service = ReviewService(db)
        
        # Analyze sentiment
        sentiment_result = ml_service.analyze_sentiment(request.text)
        
        # Save to database
        review_data = ReviewCreate(
            text=request.text,
            sentiment=sentiment_result["sentiment"],
            confidence=sentiment_result["confidence"]
        )
        
        review = review_service.create_review(review_data)
        
        return ReviewResponse(
            id=review.id,
            text=review.text,
            sentiment=review.sentiment,
            confidence=review.confidence,
            created_at=review.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ReviewResponse])
async def get_reviews(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of analyzed reviews.
    """
    review_service = ReviewService(db)
    reviews = review_service.get_reviews(skip=skip, limit=limit)
    
    return [
        ReviewResponse(
            id=review.id,
            text=review.text,
            sentiment=review.sentiment,
            confidence=review.confidence,
            created_at=review.created_at
        )
        for review in reviews
    ]


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific review by ID.
    """
    review_service = ReviewService(db)
    review = review_service.get_review(review_id)
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return ReviewResponse(
        id=review.id,
        text=review.text,
        sentiment=review.sentiment,
        confidence=review.confidence,
        created_at=review.created_at
    )
