"""
Database dependencies for FastAPI dependency injection.

This module provides:
- Database session dependency
- Repository factory functions
- Transaction management utilities
"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.db.base import get_session_factory
from app.infra.db.repo import TaskRepository, UserSessionRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency for FastAPI.
    
    Yields:
        Database session with automatic transaction management
    """
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_task_repository(
    session: AsyncSession = Depends(get_db_session)
) -> TaskRepository:
    """
    Get task repository instance.
    
    Args:
        session: Database session from dependency
        
    Returns:
        TaskRepository instance
    """
    return TaskRepository(session)


def get_user_session_repository(
    session: AsyncSession = Depends(get_db_session)
) -> UserSessionRepository:
    """
    Get user session repository instance.
    
    Args:
        session: Database session from dependency
        
    Returns:
        UserSessionRepository instance
    """
    return UserSessionRepository(session)
