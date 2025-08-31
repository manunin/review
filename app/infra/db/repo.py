"""
Repository pattern implementation for database operations.

This module provides:
- TaskRepository with async methods
- CRUD operations for tasks
- User-specific task queries
- Session management utilities
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infra.db.models import Task, TaskStatus, TaskType, UserSession


class TaskRepository:
    """Repository for Task model operations."""
    
    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.
        
        Args:
            session: Async database session
        """
        self.session = session
    
    async def create(
        self,
        task_type: TaskType,
        user_id: str,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """
        Create a new task.
        
        Args:
            task_type: Type of task (single/batch)
            user_id: User identifier
            extra_data: Additional task metadata
            
        Returns:
            Created task instance
        """
        task = Task(
            type=task_type,
            user_id=user_id,
            status=TaskStatus.ACCEPTED,
            extra_data=extra_data or {},
        )
        
        self.session.add(task)
        await self.session.flush()  # Get the ID without committing
        return task
    
    async def get_by_id(self, task_id: int) -> Optional[Task]:
        """
        Get task by internal ID.
        
        Args:
            task_id: Internal task ID
            
        Returns:
            Task instance or None if not found
        """
        stmt = select(Task).where(Task.id == task_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_task_id(self, task_id: uuid.UUID) -> Optional[Task]:
        """
        Get task by external task ID.
        
        Args:
            task_id: External task UUID
            
        Returns:
            Task instance or None if not found
        """
        stmt = select(Task).where(Task.task_id == task_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_tasks(
        self,
        user_id: str,
        task_type: Optional[TaskType] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Task]:
        """
        Get tasks for a specific user.
        
        Args:
            user_id: User identifier
            task_type: Filter by task type (optional)
            status: Filter by task status (optional)
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip
            
        Returns:
            List of tasks
        """
        stmt = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(desc(Task.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        if task_type:
            stmt = stmt.where(Task.type == task_type)
        
        if status:
            stmt = stmt.where(Task.status == status)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_last_user_task(
        self,
        user_id: str,
        task_type: TaskType,
    ) -> Optional[Task]:
        """
        Get the most recent task for a user of a specific type.
        
        Args:
            user_id: User identifier
            task_type: Type of task to find
            
        Returns:
            Most recent task or None if not found
        """
        stmt = (
            select(Task)
            .where(Task.user_id == user_id)
            .where(Task.type == task_type)
            .order_by(desc(Task.created_at))
            .limit(1)
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_status(
        self,
        task_id: int,
        status: TaskStatus,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Optional[Task]:
        """
        Update task status and timing.
        
        Args:
            task_id: Internal task ID
            status: New task status
            start_time: Task start time (optional)
            end_time: Task end time (optional)
            
        Returns:
            Updated task instance or None if not found
        """
        update_data: Dict[str, Any] = {"status": status}
        
        if start_time:
            update_data["start_time"] = start_time
        
        if end_time:
            update_data["end_time"] = end_time
        
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(**update_data)
            .returning(Task)
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_result(
        self,
        task_id: int,
        result: Dict[str, Any],
        status: TaskStatus = TaskStatus.READY,
        end_time: Optional[datetime] = None,
    ) -> Optional[Task]:
        """
        Update task result and mark as completed.
        
        Args:
            task_id: Internal task ID
            result: Task result data
            status: Task status (default: READY)
            end_time: Task completion time
            
        Returns:
            Updated task instance or None if not found
        """
        update_data: Dict[str, Any] = {
            "result": result,
            "status": status,
        }
        
        if end_time:
            update_data["end_time"] = end_time
        else:
            update_data["end_time"] = datetime.utcnow()
        
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(**update_data)
            .returning(Task)
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_error(
        self,
        task_id: int,
        error: Dict[str, Any],
        end_time: Optional[datetime] = None,
    ) -> Optional[Task]:
        """
        Update task with error information.
        
        Args:
            task_id: Internal task ID
            error: Error information
            end_time: Task failure time
            
        Returns:
            Updated task instance or None if not found
        """
        update_data: Dict[str, Any] = {
            "error": error,
            "status": TaskStatus.ERROR,
        }
        
        if end_time:
            update_data["end_time"] = end_time
        else:
            update_data["end_time"] = datetime.utcnow()
        
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(**update_data)
            .returning(Task)
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_tasks_by_status(
        self,
        status: TaskStatus,
        limit: int = 100,
    ) -> List[Task]:
        """
        Get tasks by status for background processing.
        
        Args:
            status: Task status to filter by
            limit: Maximum number of tasks to return
            
        Returns:
            List of tasks with specified status
        """
        stmt = (
            select(Task)
            .where(Task.status == status)
            .order_by(Task.created_at)
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def count_user_tasks(
        self,
        user_id: str,
        task_type: Optional[TaskType] = None,
        status: Optional[TaskStatus] = None,
    ) -> int:
        """
        Count tasks for a user.
        
        Args:
            user_id: User identifier
            task_type: Filter by task type (optional)
            status: Filter by task status (optional)
            
        Returns:
            Number of tasks matching criteria
        """
        stmt = select(Task).where(Task.user_id == user_id)
        
        if task_type:
            stmt = stmt.where(Task.type == task_type)
        
        if status:
            stmt = stmt.where(Task.status == status)
        
        result = await self.session.execute(stmt)
        return len(list(result.scalars().all()))


class UserSessionRepository:
    """Repository for UserSession model operations."""
    
    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.
        
        Args:
            session: Async database session
        """
        self.session = session
    
    async def create_or_update(
        self,
        session_id: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> UserSession:
        """
        Create a new session or update existing one.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            ip_address: User IP address
            user_agent: User agent string
            extra_data: Additional session metadata
            
        Returns:
            UserSession instance
        """
        # Try to find existing session
        stmt = select(UserSession).where(UserSession.session_id == session_id)
        result = await self.session.execute(stmt)
        user_session = result.scalar_one_or_none()
        
        if user_session:
            # Update existing session
            user_session.last_activity = datetime.utcnow()
            if ip_address:
                user_session.ip_address = ip_address
            if user_agent:
                user_session.user_agent = user_agent
            if extra_data:
                user_session.extra_data = extra_data
        else:
            # Create new session
            user_session = UserSession(
                session_id=session_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                extra_data=extra_data or {},
            )
            self.session.add(user_session)
        
        await self.session.flush()
        return user_session
    
    async def get_by_session_id(self, session_id: str) -> Optional[UserSession]:
        """
        Get session by session ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            UserSession instance or None if not found
        """
        stmt = select(UserSession).where(UserSession.session_id == session_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10,
    ) -> List[UserSession]:
        """
        Get sessions for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return
            
        Returns:
            List of user sessions
        """
        stmt = (
            select(UserSession)
            .where(UserSession.user_id == user_id)
            .order_by(desc(UserSession.last_activity))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def cleanup_old_sessions(self, older_than: datetime) -> int:
        """
        Remove sessions older than specified date.
        
        Args:
            older_than: Cutoff datetime
            
        Returns:
            Number of deleted sessions
        """
        stmt = select(UserSession).where(UserSession.last_activity < older_than)
        result = await self.session.execute(stmt)
        sessions_to_delete = list(result.scalars().all())
        
        for session in sessions_to_delete:
            await self.session.delete(session)
        
        return len(sessions_to_delete)
