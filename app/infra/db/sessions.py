"""
User session model for the Review Analysis API infrastructure.

This module contains:
- UserSession model for session tracking
- Proper indexes and constraints for session management
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import JSON, DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


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
