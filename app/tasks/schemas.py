"""
Pydantic schemas for tasks API according to OpenAPI specification.
"""
from typing import Any, Optional, Dict, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import re


# Enums according to OpenAPI specification
class TaskTypeEnum(str, Enum):
    """Task type enumeration."""
    single = "single"
    batch = "batch"


class TaskStatusEnum(str, Enum):
    """Task status enumeration."""
    accepted = "accepted"
    queued = "queued"
    ready = "ready"
    error = "error"


class SentimentEnum(str, Enum):
    """Sentiment analysis result enumeration."""
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class TaskErrorCodeEnum(str, Enum):
    """Task error code enumeration."""
    code_01 = "01"
    code_02 = "02"
    code_03 = "03"


def validate_user_id(v: str) -> str:
    """Validate and sanitize user_id."""
    if not v or not v.strip():
        raise ValueError("User ID cannot be empty or whitespace only")
    
    # Remove dangerous characters including null bytes
    if '\x00' in v:
        raise ValueError("User ID cannot contain null bytes")
    
    # Check for other control characters
    if any(ord(c) < 32 for c in v if c not in ['\t']):
        raise ValueError("User ID cannot contain control characters")
    
    # Check for potentially dangerous characters that could be used in attacks
    # Keep only the most dangerous ones, allow common punctuation
    dangerous_chars = ['<', '>', ';', '&', '|', '`', '$']
    if any(char in v for char in dangerous_chars):
        raise ValueError("User ID contains potentially dangerous characters")
    
    # Check for SQL injection patterns
    sql_patterns = ['drop', 'select', 'insert', 'update', 'delete', 'union', 'script']
    v_lower = v.lower()
    if any(pattern in v_lower for pattern in sql_patterns):
        raise ValueError("User ID contains potentially dangerous SQL keywords")
    
    # Remove leading/trailing whitespace
    v = v.strip()
    
    if len(v) == 0:
        raise ValueError("User ID cannot be empty after sanitization")
        
    return v


# Request schemas
class SingleTaskResultRequest(BaseModel):
    """Request schema for getting single task result."""
    user_id: str = Field(..., min_length=1, max_length=255, description="User identification from cookies", example="some cookies id")
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id_field(cls, v: str) -> str:
        return validate_user_id(v)


class BatchTaskResultRequest(BaseModel):
    """Request schema for getting batch task result."""
    user_id: str = Field(..., min_length=1, max_length=255, description="User identification from cookies", example="some cookies id")
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id_field(cls, v: str) -> str:
        return validate_user_id(v)


class SingleTaskRequest(BaseModel):
    """Request schema for single text analysis task."""
    user_id: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="User identifier"
    )
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=512,
        description="Text to analyze (max 512 characters)"
    )
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id_field(cls, v: str) -> str:
        return validate_user_id(v)
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate and sanitize text input."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        
        # Remove null bytes
        if '\x00' in v:
            v = v.replace('\x00', '')
        
        # Check for potentially dangerous script content
        dangerous_patterns = [
            '<script',
            'javascript:',
            'onerror=',
            'onload=',
            'onclick=',
            'onmouseover=',
            'DROP TABLE',
            'DELETE FROM',
            'INSERT INTO',
            'UPDATE SET',
            'UNION SELECT',
            "' OR '1'='1",
            "'; --",
        ]
        
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in v_lower:
                raise ValueError(f"Text contains potentially dangerous content: {pattern}")
        
        # Check for excessive length after sanitization
        v = v.strip()
        if len(v) == 0:
            raise ValueError("Text cannot be empty after sanitization")
            
        return v


# Result schemas according to OpenAPI specification
class SingleResult(BaseModel):
    """Single text analysis result schema."""
    sentiment: SentimentEnum = Field(..., description="Sentiment analysis result")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence in analysis result")
    text: Optional[str] = Field(None, description="Analyzed text (optional)")


class BatchResult(BaseModel):
    """Batch analysis result schema."""
    total_reviews: int = Field(..., ge=0, description="Total number of reviews processed")
    positive: int = Field(..., ge=0, description="Number of positive reviews")
    negative: int = Field(..., ge=0, description="Number of negative reviews")
    neutral: int = Field(..., ge=0, description="Number of neutral reviews")
    positive_percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of positive reviews")
    negative_percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of negative reviews")
    neutral_percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of neutral reviews")


class TaskError(BaseModel):
    """Task error schema."""
    code: TaskErrorCodeEnum = Field(..., description="Error code")
    description: Optional[str] = Field(None, description="Backend error description (optional)")


class Task(BaseModel):
    """Main task response schema according to OpenAPI specification."""
    task_id: str = Field(..., description="Unique task identifier", example="123e4567-e89b-12d3-a456-426614174000")
    type: TaskTypeEnum = Field(..., description="Task type")
    status: TaskStatusEnum = Field(..., description="Task status")
    start: int = Field(..., description="Unix timestamp of task start")
    end: Optional[int] = Field(None, description="Unix timestamp of task completion (optional)")
    result: Optional[Union[SingleResult, BatchResult]] = Field(None, description="Task result (depends on task type)")
    error: Optional[TaskError] = Field(None, description="Task error information")


# Error schemas according to OpenAPI specification
class ApiError(BaseModel):
    """API error response according to OpenAPI specification."""
    message: str = Field(..., description="Error description")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ValidationError(BaseModel):
    """Validation error response according to OpenAPI specification."""
    message: str = Field(..., description="General validation error description")
    details: Optional[Dict[str, list[str]]] = Field(None, description="Detailed validation error information by fields")