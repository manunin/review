"""
Task Management Module - FastAPI Dependencies.

This module contains:
- Task service injection
- User ID extraction
- Database session management
"""

# todo implement dependencies

from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.db.dependencies import get_db_session, get_task_repository
from app.infra.db.repo import TaskRepository
from app.tasks.service import TaskService


async def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repository)
) -> TaskService:
    """
    Get task service instance with repository injection.
    
    Args:
        task_repo: Task repository from dependency
        
    Returns:
        TaskService instance
    """
    return TaskService(task_repo)


async def extract_user_id_from_header(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
) -> str:
    """
    Extract user ID from request headers.
    
    Args:
        x_user_id: User ID from X-User-ID header
        
    Returns:
        User ID string
        
    Raises:
        HTTPException: If user ID is missing
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User identification required. Provide X-User-ID header."
        )
    
    return x_user_id


async def extract_user_id_from_cookie(
    # This would typically extract from cookies in a real implementation
    # For now, we'll use a placeholder
    user_id: Optional[str] = None
) -> str:
    """
    Extract user ID from cookies (placeholder implementation).
    
    Args:
        user_id: User ID from cookies
        
    Returns:
        User ID string
        
    Raises:
        HTTPException: If user ID is missing
    """
    # In a real implementation, this would extract from request cookies
    # For now, we'll require it to be provided via request body
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User identification required in request body."
        )
    
    return user_id


async def get_current_user_id() -> str:
    """
    Get current user ID using the configured extraction method.
    
    For this implementation, we expect user_id in request body
    as specified in the OpenAPI spec.
    
    Returns:
        User ID string
    """
    # This dependency will be used by endpoints to validate user presence
    # The actual user_id will come from request body validation
    # This is mainly for documentation and consistency
    return "user_from_request_body"


# Database transaction decorator
class DatabaseTransaction:
    """Context manager for database transactions."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def __aenter__(self):
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()


async def get_db_transaction(
    session: AsyncSession = Depends(get_db_session)
) -> DatabaseTransaction:
    """
    Get database transaction context manager.
    
    Args:
        session: Database session from dependency
        
    Returns:
        Transaction context manager
    """
    return DatabaseTransaction(session)


# Validation dependencies
async def validate_task_access(
    user_id: str,
    task_user_id: str
) -> bool:
    """
    Validate that user has access to the task.
    
    Args:
        user_id: Current user ID
        task_user_id: Task owner user ID
        
    Returns:
        True if access is allowed
        
    Raises:
        HTTPException: If access is denied
    """
    if user_id != task_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Task belongs to different user."
        )
    
    return True


# Rate limiting (placeholder for future implementation)
async def rate_limit_user(user_id: str) -> bool:
    """
    Apply rate limiting for user requests.
    
    Args:
        user_id: User identifier
        
    Returns:
        True if request is allowed
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    # Placeholder for rate limiting implementation
    # In production, this would check Redis or similar store
    return True
