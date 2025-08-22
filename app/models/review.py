"""
SQLAlchemy models for the Smart Review Analyzer
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Review(Base):
    """Review model for storing analyzed reviews."""
    
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False, comment="Original review text")
    sentiment = Column(String(20), nullable=False, comment="Predicted sentiment: positive, negative, neutral")
    confidence = Column(Float, nullable=False, comment="Model confidence score (0-1)")
    source = Column(String(100), nullable=True, comment="Source of the review (file, API, etc.)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Timestamp when review was analyzed")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="Timestamp of last update")
    
    def __repr__(self):
        return f"<Review(id={self.id}, sentiment='{self.sentiment}', confidence={self.confidence})>"


class AnalysisSession(Base):
    """Model for tracking batch analysis sessions."""
    
    __tablename__ = "analysis_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=True, comment="Original filename if uploaded from file")
    total_reviews = Column(Integer, nullable=False, default=0, comment="Total number of reviews in this session")
    positive_count = Column(Integer, nullable=False, default=0, comment="Number of positive reviews")
    negative_count = Column(Integer, nullable=False, default=0, comment="Number of negative reviews")
    neutral_count = Column(Integer, nullable=False, default=0, comment="Number of neutral reviews")
    avg_confidence = Column(Float, nullable=True, comment="Average confidence score for this session")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Session creation timestamp")
    
    def __repr__(self):
        return f"<AnalysisSession(id={self.id}, total_reviews={self.total_reviews})>"
