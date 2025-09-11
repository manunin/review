"""
SQLAlchemy models for tasks domain.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Index, String, Text, func, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class TaskType(str, Enum):
    """Task types supported by the system."""
    single = "single"
    batch = "batch"


class TaskStatus(str, Enum):
    """Task status lifecycle."""
    accepted = "accepted"
    queued = "queued"
    ready = "ready"
    error = "error"


class SentimentEnum(str, Enum):
    """Sentiment analysis results."""
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class TaskErrorCode(str, Enum):
    """Task error codes according to OpenAPI spec."""
    code_01 = "01"
    code_02 = "02"
    code_03 = "03"


class Task(Base):
    """
    Task model for storing analysis tasks and results according to OpenAPI spec.
    """
    __tablename__ = "tasks"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Task identification (UUID as string for API compatibility)
    task_id: Mapped[str] = mapped_column(
        String(36),
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique task identifier"
    )
    
    # Task properties
    type: Mapped[TaskType] = mapped_column(
        String(10),
        nullable=False,
        comment="Task type: single or batch"
    )
    
    status: Mapped[TaskStatus] = mapped_column(
        String(20),
        nullable=False,
        default=TaskStatus.accepted,
        index=True,
        comment="Current task status"
    )
    
    # User identification
    user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="User identifier from cookies"
    )
    
    # Timestamps as Unix timestamps for API compatibility
    start: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Unix timestamp of task start"
    )
    
    end: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Unix timestamp of task completion"
    )
    
    # Input data
    text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Input text for single analysis"
    )
    
    file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="File path for batch analysis"
    )
    
    # Single analysis results
    sentiment: Mapped[Optional[SentimentEnum]] = mapped_column(
        String(20),
        nullable=True,
        comment="Sentiment analysis result"
    )
    
    confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Model confidence in analysis result"
    )
    
    # Batch analysis results
    total_reviews: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Total number of reviews processed"
    )
    
    positive: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of positive reviews"
    )
    
    negative: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of negative reviews"
    )
    
    neutral: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of neutral reviews"
    )
    
    positive_percentage: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Percentage of positive reviews"
    )
    
    negative_percentage: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Percentage of negative reviews"
    )
    
    neutral_percentage: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Percentage of neutral reviews"
    )
    
    # Error information
    error_code: Mapped[Optional[TaskErrorCode]] = mapped_column(
        String(5),
        nullable=True,
        comment="Error code if task failed"
    )
    
    error_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error description if task failed"
    )
    
    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        comment="Task creation timestamp (UTC)"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        comment="Last update timestamp (UTC)"
    )
    
    # Indexes for optimal query performance
    __table_args__ = (
        Index("idx_tasks_user_type_status", "user_id", "type", "status"),
        Index("idx_tasks_created_at", "created_at"),
        Index("idx_tasks_status_updated", "status", "updated_at"),
    )
    
    def __repr__(self) -> str:
        """String representation of Task."""
        return (
            f"<Task(id={self.id}, task_id={self.task_id}, "
            f"type={self.type}, status={self.status}, user_id={self.user_id[:8]}...)>"
        )