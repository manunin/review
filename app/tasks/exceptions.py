"""
Task Management Module - Exceptions.

This module contains:
- TaskNotFound, InvalidTaskStatus
- FileProcessingError, UnsupportedFormat
- Error code mapping ("01", "02", "03")
"""

from typing import Optional
from enum import Enum

from app.core.exceptions import BaseAppException

class ErrorCode(str, Enum):
    """Error codes for task processing failures."""
    
    PROCESSING_ERROR = "01"      # General processing error
    INVALID_INPUT = "02"         # Invalid input data
    SYSTEM_ERROR = "03"          # System/infrastructure error

class TaskException(BaseAppException):
    """Base exception for task-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[ErrorCode] = None,
        details: Optional[dict] = None,
    ) -> None:
        super().__init__(message, details)
        self.error_code = error_code or ErrorCode.SYSTEM_ERROR


class TaskNotFound(TaskException):
    """Raised when a task is not found."""
    
    def __init__(self, task_id: str, task_type: Optional[str] = None) -> None:
        message = f"Task not found: {task_id}"
        if task_type:
            message = f"No {task_type} task found for this user"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_INPUT,
            details={"task_id": task_id, "task_type": task_type}
        )
        # Override status code to 404 for not found errors
        self.status_code = 404


class InvalidTaskStatus(TaskException):
    """Raised when task status transition is invalid."""
    
    def __init__(self, current_status: str, requested_status: str) -> None:
        super().__init__(
            message=f"Invalid status transition from {current_status} to {requested_status}",
            error_code=ErrorCode.INVALID_INPUT,
            details={
                "current_status": current_status,
                "requested_status": requested_status
            }
        )


class FileProcessingError(TaskException):
    """Raised when file processing fails."""
    
    def __init__(self, filename: str, reason: str) -> None:
        super().__init__(
            message=f"Failed to process file {filename}: {reason}",
            error_code=ErrorCode.PROCESSING_ERROR,
            details={"filename": filename, "reason": reason}
        )


class UnsupportedFormat(TaskException):
    """Raised when file format is not supported."""
    
    def __init__(self, filename: str, format_type: str) -> None:
        super().__init__(
            message=f"Unsupported file format: {format_type} for file {filename}",
            error_code=ErrorCode.INVALID_INPUT,
            details={"filename": filename, "format": format_type}
        )
        # Override status code to 415 for unsupported media type
        self.status_code = 415


class TextTooLong(TaskException):
    """Raised when input text exceeds maximum length."""
    
    def __init__(self, text_length: int, max_length: int) -> None:
        super().__init__(
            message=f"Text length {text_length} exceeds maximum {max_length} characters",
            error_code=ErrorCode.INVALID_INPUT,
            details={"text_length": text_length, "max_length": max_length}
        )


class FileTooLarge(TaskException):
    """Raised when uploaded file exceeds size limit."""
    
    def __init__(self, file_size: int, max_size: int, filename: str) -> None:
        super().__init__(
            message=f"File size exceeds the maximum limit of 10MB.",
            error_code=ErrorCode.INVALID_INPUT,
            details={
                "filename": filename,
                "file_size": file_size,
                "max_size": max_size
            }
        )
        # Override status code to 413 for payload too large
        self.status_code = 413


class TaskProcessingTimeout(TaskException):
    """Raised when task processing times out."""
    
    def __init__(self, task_id: str, timeout_seconds: int) -> None:
        super().__init__(
            message=f"Task {task_id} processing timed out after {timeout_seconds} seconds",
            error_code=ErrorCode.PROCESSING_ERROR,
            details={"task_id": task_id, "timeout_seconds": timeout_seconds}
        )
