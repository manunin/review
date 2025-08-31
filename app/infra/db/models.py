"""
ORM models for the Review Analysis API.

This module contains:
- Task model (UUID, type, status, timestamps, user_id, result)
- User session tracking model
- Proper indexes and constraints
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import JSON, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class TaskType(str, Enum):
    """Task types supported by the system."""
    
    SINGLE = "single"
    BATCH = "batch"


class TaskStatus(str, Enum):
    """Task status lifecycle."""
    
    ACCEPTED = "accepted"  # Task created and accepted
    QUEUED = "queued"      # Task queued for processing
    PROCESSING = "processing"  # Task is being processed
    READY = "ready"        # Task completed successfully
    ERROR = "error"        # Task failed with error


class Task(Base):
    """
    Task model for storing analysis tasks and results.
    
    Attributes:
        id: Primary key UUID
        task_id: External task identifier (UUID)
        type: Task type (single/batch)
        status: Current task status
        user_id: User identifier from cookies/headers
        created_at: Task creation timestamp (UTC)
        updated_at: Last update timestamp (UTC)
        start_time: Task processing start time
        end_time: Task processing end time
        result: Task result data (JSON)
        error: Error information if task failed
        extra_data: Additional task metadata
    """
    
    __tablename__ = "tasks"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Task identification
    task_id: Mapped[uuid.UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
        comment="External task identifier"
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
        default=TaskStatus.ACCEPTED,
        index=True,
        comment="Current task status"
    )
    
    # User identification
    user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="User identifier from cookies/headers"
    )
    
    # Timestamps
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
    
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Task processing start time"
    )
    
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Task processing end time"
    )
    
    # Task data
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Task result data (JSON)"
    )
    
    error: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Error information if task failed"
    )
    
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional task metadata"
    )
    
    # Indexes for optimal query performance
    __table_args__ = (
        # Composite index for user queries
        Index("idx_tasks_user_type_status", "user_id", "type", "status"),
        # Index for time-based queries
        Index("idx_tasks_created_at", "created_at"),
        # Index for status monitoring
        Index("idx_tasks_status_updated", "status", "updated_at"),
    )
    
    def __repr__(self) -> str:
        """String representation of Task."""
        return (
            f"<Task(id={self.id}, task_id={self.task_id}, "
            f"type={self.type}, status={self.status}, user_id={self.user_id[:8]}...)>"
        )


class UserSession(Base):
    """
    User session tracking model for analytics and monitoring.
    
    Attributes:
        id: Primary key
        session_id: Session identifier
        user_id: User identifier
        created_at: Session creation time
        last_activity: Last activity timestamp
        ip_address: User IP address (optional)
        user_agent: User agent string (optional)
        extra_data: Additional session metadata
    """
    
    __tablename__ = "user_sessions"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Session identification
    session_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Session identifier"
    )
    
    user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="User identifier"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        comment="Session creation timestamp (UTC)"
    )
    
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        comment="Last activity timestamp (UTC)"
    )
    
    # Optional tracking data
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # Support IPv6
        nullable=True,
        comment="User IP address"
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User agent string"
    )
    
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional session metadata"
    )
    
    # Indexes for session queries
    __table_args__ = (
        # Index for user session lookup
        Index("idx_user_sessions_user_activity", "user_id", "last_activity"),
        # Index for session cleanup
        Index("idx_user_sessions_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        """String representation of UserSession."""
        return (
            f"<UserSession(id={self.id}, session_id={self.session_id[:8]}..., "
            f"user_id={self.user_id[:8]}..., last_activity={self.last_activity})>"
        )
