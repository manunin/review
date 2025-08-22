"""
Pydantic schemas for review data validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReviewAnalyzeRequest(BaseModel):
    """Request schema for analyzing a single review."""
    text: str = Field(..., min_length=1, max_length=5000, description="Review text to analyze")


class ReviewCreate(BaseModel):
    """Schema for creating a new review."""
    text: str = Field(..., min_length=1, max_length=5000)
    sentiment: str = Field(..., description="Sentiment: positive, negative, or neutral")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    source: Optional[str] = Field(None, description="Source of the review")


class ReviewResponse(BaseModel):
    """Response schema for review data."""
    id: int
    text: str
    sentiment: str
    confidence: float
    created_at: datetime
    source: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReviewUpdate(BaseModel):
    """Schema for updating review data."""
    sentiment: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    source: Optional[str] = None
