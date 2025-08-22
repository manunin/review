"""
Review service for database operations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.review import Review, AnalysisSession
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewService:
    """Service for review-related database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_review(self, review_data: ReviewCreate) -> Review:
        """Create a new review in the database."""
        db_review = Review(
            text=review_data.text,
            sentiment=review_data.sentiment,
            confidence=review_data.confidence,
            source=review_data.source
        )
        self.db.add(db_review)
        self.db.commit()
        self.db.refresh(db_review)
        return db_review
    
    def get_review(self, review_id: int) -> Optional[Review]:
        """Get a review by ID."""
        return self.db.query(Review).filter(Review.id == review_id).first()
    
    def get_reviews(self, skip: int = 0, limit: int = 100) -> List[Review]:
        """Get a list of reviews with pagination."""
        return self.db.query(Review).offset(skip).limit(limit).all()
    
    def update_review(self, review_id: int, review_data: ReviewUpdate) -> Optional[Review]:
        """Update a review."""
        db_review = self.get_review(review_id)
        if db_review:
            for field, value in review_data.dict(exclude_unset=True).items():
                setattr(db_review, field, value)
            self.db.commit()
            self.db.refresh(db_review)
        return db_review
    
    def delete_review(self, review_id: int) -> bool:
        """Delete a review."""
        db_review = self.get_review(review_id)
        if db_review:
            self.db.delete(db_review)
            self.db.commit()
            return True
        return False
    
    def get_reviews_by_sentiment(self, sentiment: str) -> List[Review]:
        """Get reviews filtered by sentiment."""
        return self.db.query(Review).filter(Review.sentiment == sentiment).all()
    
    def get_sentiment_statistics(self) -> dict:
        """Get overall sentiment statistics."""
        total_reviews = self.db.query(Review).count()
        
        if total_reviews == 0:
            return {
                "total_reviews": 0,
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "positive_percentage": 0,
                "negative_percentage": 0,
                "neutral_percentage": 0
            }
        
        positive_count = self.db.query(Review).filter(Review.sentiment == "positive").count()
        negative_count = self.db.query(Review).filter(Review.sentiment == "negative").count()
        neutral_count = self.db.query(Review).filter(Review.sentiment == "neutral").count()
        
        return {
            "total_reviews": total_reviews,
            "positive": positive_count,
            "negative": negative_count,
            "neutral": neutral_count,
            "positive_percentage": round((positive_count / total_reviews) * 100, 2),
            "negative_percentage": round((negative_count / total_reviews) * 100, 2),
            "neutral_percentage": round((neutral_count / total_reviews) * 100, 2)
        }
