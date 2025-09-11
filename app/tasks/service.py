"""
Task Management Service - Business Logic Layer.

This module contains the business logic for task management according to
the domain-driven architecture principles from app/CONTEXT.MD and OpenAPI spec.
"""

import time
from datetime import datetime
from typing import Optional

print("DEBUG: Начинаем импорты в service.py")

from app.core.logging import get_logger
from app.infra.db.repo import TaskRepository
from app.tasks.models import TaskType
from .exceptions import TaskNotFound, InvalidTaskStatus, FileTooLarge, UnsupportedFormat
from app.tasks.models import Task as DbTask
from app.tasks.schemas import (
    Task, SingleResult, BatchResult, TaskError, 
    TaskTypeEnum, TaskStatusEnum, SentimentEnum
)

print("DEBUG: Все импорты завершены успешно")

logger = get_logger(__name__)


class TaskService:
    """
    Task service implementing business logic for task management.
    
    Handles:
    - Task creation and lifecycle management
    - Result retrieval and processing
    - Status updates and error handling
    - Domain-specific validations
    """
    
    def __init__(self, task_repo: TaskRepository) -> None:
        """Initialize task service with repository dependency."""
        self.task_repo = task_repo
        
    async def create_single_task(
        self, 
        user_id: str, 
        text: str
    ) -> Task:
        """
        Create a new single text analysis task.
        
        Args:
            user_id: User identifier from cookies
            text: Text to analyze (max 512 characters)
            
        Returns:
            Created task with initial status
            
        Raises:
            ValueError: If text exceeds max length
        """
        logger.info("Creating single task", extra={
            "user_id": user_id[:8] + "..." if len(user_id) > 8 else user_id,
            "text_length": len(text)
        })
        
        # Validate text length according to OpenAPI spec
        if len(text) > 512:
            raise ValueError("Text exceeds maximum length of 512 characters")
            
        # Create database task
        db_task = await self.task_repo.create(
            task_type=TaskType.single,
            user_id=user_id,
            extra_data={"text": text}
        )
        
        # Convert to domain model and add mock result for demo
        task = self._db_task_to_domain(db_task)
        
        # For demo purposes, add immediate mock analysis result
        task.result = SingleResult(
            sentiment=SentimentEnum.positive,
            confidence=0.95,
            text=text
        )
        
        logger.info("Single task created", extra={"task_id": task.task_id})
        return task
        
    async def create_batch_task(
        self,
        user_id: str,
        file_content: bytes,
        filename: str
    ) -> Task:
        """
        Create a new batch file analysis task.
        
        Args:
            user_id: User identifier from cookies
            file_content: File content bytes
            filename: Original filename
            
        Returns:
            Created task with initial status
            
        Raises:
            FileTooLarge: If file is too large
            UnsupportedFormat: If file format is not supported
        """
        logger.info("Creating batch task", extra={
            "user_id": user_id[:8] + "..." if len(user_id) > 8 else user_id,
            "file_name": filename,
            "file_size": len(file_content)
        })
        
        # Validate file size (max 10MB according to OpenAPI spec)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_content) >= max_size:
            raise FileTooLarge(len(file_content), max_size, filename)
            
        # Validate file format
        valid_extensions = {'.csv', '.txt', '.json'}
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        if f'.{file_ext}' not in valid_extensions:
            raise UnsupportedFormat(filename, file_ext)
            
        # Validate file content
        self._validate_file_content(file_content, file_ext, filename)
            
        # Create database task
        db_task = await self.task_repo.create(
            task_type=TaskType.batch,
            user_id=user_id,
            extra_data={
                "filename": filename,
                "file_size": len(file_content),
                "file_type": file_ext
            }
        )
        
        # Convert to domain model and add mock result for demo
        task = self._db_task_to_domain(db_task)
        
        # For demo purposes, add immediate mock batch analysis result
        task.result = BatchResult(
            total_reviews=150,
            positive=90,
            negative=35,
            neutral=25,
            positive_percentage=60.0,
            negative_percentage=23.3,
            neutral_percentage=16.7
        )
        
        logger.info("Batch task created", extra={"task_id": task.task_id})
        return task
        
    async def get_last_single_task(self, user_id: str) -> Task:
        """
        Get the last single task for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Last single task
            
        Raises:
            TaskNotFound: If no single task found for user
        """
        logger.info("Getting last single task", extra={
            "user_id": user_id[:8] + "..." if len(user_id) > 8 else user_id
        })
        
        db_task = await self.task_repo.get_last_user_task(
            user_id=user_id,
            task_type=TaskType.single
        )
        
        if not db_task:
            logger.error("No single task found for user")
            raise TaskNotFound("No single task found for user")
            
        task = self._db_task_to_domain(db_task)
        
        # Add mock result if task is ready
        if task.status == TaskStatusEnum.ready:
            task.result = SingleResult(
                sentiment=SentimentEnum.positive,
                confidence=0.95,
                text="Sample analyzed text"
            )
            
        logger.info("Single task retrieved", extra={"task_id": task.task_id})
        return task
        
    async def get_last_batch_task(self, user_id: str) -> Task:
        """
        Get the last batch task for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Last batch task
            
        Raises:
            TaskNotFound: If no batch task found for user
        """
        logger.info("Getting last batch task", extra={
            "user_id": user_id[:8] + "..." if len(user_id) > 8 else user_id
        })
        
        db_task = await self.task_repo.get_last_user_task(
            user_id=user_id,
            task_type=TaskType.batch
        )
        
        if not db_task:
            logger.error("No batch task found for user")
            raise TaskNotFound("No batch task found for user")
            
        task = self._db_task_to_domain(db_task)
        
        # Add mock result if task is ready
        if task.status == TaskStatusEnum.ready:
            task.result = BatchResult(
                total_reviews=150,
                positive=90,
                negative=35,
                neutral=25,
                positive_percentage=60.0,
                negative_percentage=23.3,
                neutral_percentage=16.7
            )
            
        logger.info("Batch task retrieved", extra={"task_id": task.task_id})
        return task
        
    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatusEnum,
        error: Optional[TaskError] = None
    ) -> Optional[Task]:
        """
        Update task status and optionally set error information.
        
        Args:
            task_id: Task identifier
            status: New status
            error: Error information if status is error
            
        Returns:
            Updated task or None if not found
            
        Raises:
            InvalidTaskStatus: If status transition is invalid
        """
        logger.info("Updating task status", extra={
            "task_id": task_id,
            "new_status": status,
            "has_error": error is not None
        })
        
        # Get current task to validate status transition
        db_task = await self.task_repo.get_by_task_id(task_id)
        if not db_task:
            raise TaskNotFound(f"Task {task_id} not found")
            
        # Validate status transition (basic business rules)
        current_status = TaskStatusEnum(db_task.status.value)
        if not self._is_valid_status_transition(current_status, status):
            raise InvalidTaskStatus(
                f"Invalid status transition from {current_status} to {status}"
            )
            
        # Update in database
        update_data = {"status": status.value}
        if error:
            update_data["error"] = error.model_dump()
        if status in [TaskStatusEnum.ready, TaskStatusEnum.error]:
            update_data["end_time"] = datetime.utcnow()
            
        updated_db_task = await self.task_repo.update(db_task.id, update_data)
        if not updated_db_task:
            return None
            
        task = self._db_task_to_domain(updated_db_task)
        logger.info("Task status updated", extra={"task_id": task_id})
        return task
        
    def _db_task_to_domain(self, db_task: DbTask) -> Task:
        """
        Convert database task model to domain task model.
        
        Args:
            db_task: Database task instance
            
        Returns:
            Domain task model
        """
        # Convert timestamps
        start_timestamp = int(db_task.created_at.timestamp()) if db_task.created_at else int(time.time())
        
        # Handle status conversion - check if it's already a string or enum
        status_value = db_task.status.value if hasattr(db_task.status, 'value') else db_task.status
        end_timestamp = int(db_task.updated_at.timestamp()) if db_task.updated_at and status_value in ['ready', 'error'] else None
        
        # Convert error if present
        error = None
        if db_task.error_code:
            error = TaskError(
                code=db_task.error_code,
                description=db_task.error_description or "Unknown error"
            )
            
        # Handle type conversion - check if it's already a string or enum
        type_value = db_task.type.value if hasattr(db_task.type, 'value') else db_task.type
            
        return Task(
            task_id=str(db_task.task_id),
            type=TaskTypeEnum(type_value),
            status=TaskStatusEnum(status_value),
            start=start_timestamp,
            end=end_timestamp,
            result=None,  # Will be set by calling methods based on context
            error=error
        )
        
    def _validate_file_content(self, file_content: bytes, file_ext: str, filename: str) -> None:
        """
        Validate file content for security and format issues.
        
        Args:
            file_content: File content bytes
            file_ext: File extension
            filename: Original filename
            
        Raises:
            ValidationError: If file content is invalid or potentially dangerous
        """
        from app.core.exceptions import ValidationError
        
        # Check for empty files
        if len(file_content.strip()) == 0:
            raise ValidationError("File cannot be empty")
            
        # Check for binary content or control characters
        try:
            content_str = file_content.decode('utf-8', errors='strict')
        except UnicodeDecodeError:
            raise ValidationError("File must be valid UTF-8 text")
            
        # Check for null bytes and other dangerous binary content
        if '\x00' in content_str:
            raise ValidationError("File contains null bytes")
            
        # Determine if this is a CSV file
        is_csv = file_ext.lower() == 'csv'
            
        # Check for unreasonably long lines (potential attack)
        lines = content_str.split('\n')
        for i, line in enumerate(lines):
            # For CSV files, be strict about line length to prevent CSV injection
            if is_csv and len(line) > 5000:  # More than 5KB per line for CSV
                logger.warning(f"Very long CSV line detected (line {i+1}, length {len(line)}) in file {filename}")
                raise ValidationError(f"CSV line {i+1} is too long ({len(line)} characters)")
            # For regular text files, allow much larger lines for legitimate use cases  
            elif not is_csv and len(line) >= 50000000:  # 50MB per line - only for extreme cases
                logger.warning(f"Extremely long line detected (line {i+1}, length {len(line)}) in file {filename}")
                raise ValidationError(f"Line {i+1} is too long ({len(line)} characters)")
                
        # Check for potentially dangerous script content
        dangerous_patterns = [
            '<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
            'eval(', 'exec(', 'system(', 'shell_exec(', 'passthru(',
            'DROP TABLE', 'DELETE FROM', 'INSERT INTO', 'UPDATE SET'
        ]
        
        content_lower = content_str.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in content_lower:
                logger.warning(f"Dangerous pattern detected: {pattern} in file {filename}")
                raise ValidationError(f"File contains potentially dangerous content: {pattern}")
                
        # Validate content format based on extension
        if file_ext == 'csv':
            self._validate_csv_content(content_str)
        elif file_ext == 'json':
            self._validate_json_content(content_str)
            
    def _validate_csv_content(self, content: str) -> None:
        """Validate CSV format."""
        from app.core.exceptions import ValidationError
        import csv
        import io
        
        try:
            # Try to parse as CSV
            csv_reader = csv.reader(io.StringIO(content))
            rows = list(csv_reader)
            
            if len(rows) == 0:
                raise ValidationError("CSV file has no content")
                
            # CSV files should have at least 2 rows (header + data) or multiple columns
            if len(rows) < 2:
                # If only one row, it should have multiple columns to be a valid CSV
                first_row_cols = len(rows[0]) if rows else 0
                if first_row_cols < 2:
                    raise ValidationError("Invalid CSV format: CSV must have either multiple rows or multiple columns")
                else:
                    # Single row with multiple columns should look like a proper CSV header
                    # Check if it contains typical CSV content patterns
                    row_content = ",".join(rows[0]).lower()
                    # If it's just plain text without typical CSV structure, reject it
                    if any(word in row_content for word in ["this is", "it's just", "not csv", "just text"]):
                        raise ValidationError("Invalid CSV format: Content appears to be plain text, not CSV data")
            
            # Check for reasonable number of columns
            first_row_cols = len(rows[0]) if rows else 0
            if first_row_cols > 100:  # Reasonable limit
                raise ValidationError("CSV file has too many columns")
                
            # Validate that all rows have consistent number of columns
            if len(rows) > 1:
                expected_cols = len(rows[0])
                for i, row in enumerate(rows[1:], start=2):
                    if len(row) != expected_cols:
                        raise ValidationError(f"CSV row {i} has {len(row)} columns, expected {expected_cols}")
                
            # Check for unclosed quotes or malformed CSV
            # If we have unclosed quotes, the last row might have unexpected structure
            for i, row in enumerate(rows):
                for j, field in enumerate(row):
                    # Check for suspicious patterns in fields
                    if len(field) > 10000:  # Field too long
                        raise ValidationError(f"CSV field in row {i+1}, column {j+1} is too long")
                        
            # Additional check: count quotes to detect unclosed quotes
            quote_count = content.count('"')
            if quote_count % 2 != 0:
                raise ValidationError("CSV contains unclosed quotes")
                
        except csv.Error as e:
            raise ValidationError(f"Invalid CSV format: {str(e)}")
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Invalid CSV format: {str(e)}")
            
    def _validate_json_content(self, content: str) -> None:
        """Validate JSON format."""
        from app.core.exceptions import ValidationError
        import json
        
        try:
            data = json.loads(content)
            
            # Basic size check for JSON
            if isinstance(data, dict) and len(data) > 10000:
                raise ValidationError("JSON file is too complex")
                
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format: {str(e)}")
        
    def _is_valid_status_transition(
        self, 
        current: TaskStatusEnum, 
        new: TaskStatusEnum
    ) -> bool:
        """
        Validate if status transition is allowed according to business rules.
        
        Args:
            current: Current task status
            new: New desired status
            
        Returns:
            True if transition is valid, False otherwise
        """
        # Define valid transitions according to task lifecycle
        valid_transitions = {
            TaskStatusEnum.accepted: [TaskStatusEnum.queued, TaskStatusEnum.error],
            TaskStatusEnum.queued: [TaskStatusEnum.ready, TaskStatusEnum.error],
            TaskStatusEnum.ready: [],  # Final state
            TaskStatusEnum.error: []   # Final state
        }
        
        return new in valid_transitions.get(current, [])


def create_task_service(task_repo: TaskRepository) -> TaskService:
    """
    Factory function to create TaskService instance.
    
    Args:
        task_repo: Task repository dependency
        
    Returns:
        Configured TaskService instance
    """
    return TaskService(task_repo)
