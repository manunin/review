"""
Custom exceptions and error handling following RFC 7807 Problem Details format.
"""

from __future__ import annotations

from typing import Any

from fastapi import Request

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseAppException(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        message: str = "An error occurred",
        details: dict[str, Any] | None = None,
        status_code: int = 500,
        error_type: str = "about:blank",
    ) -> None:
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(message)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert exception to RFC 7807 format."""
        problem_detail = {
            "type": self.error_type,
            "title": self.__class__.__name__,
            "status": self.status_code,
            "detail": self.message,
        }
        
        if self.details:
            problem_detail.update(self.details)
        
        return problem_detail


class ValidationError(BaseAppException):
    """Validation error (400)."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: dict[str, Any] | None = None,
        field_errors: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            details=details,
            status_code=400,
            error_type="https://api.example.com/errors/validation-error",
        )
        if field_errors:
            self.details["field_errors"] = field_errors


class NotFoundError(BaseAppException):
    """Resource not found error (404)."""
    
    def __init__(
        self,
        resource: str = "Resource",
        resource_id: str | None = None,
        message: str | None = None,
    ) -> None:
        if message is None:
            message = f"{resource} not found"
            if resource_id:
                message += f" (ID: {resource_id})"
        
        super().__init__(
            message=message,
            status_code=404,
            error_type="https://api.example.com/errors/not-found",
        )
        self.details.update({
            "resource": resource,
            "resource_id": resource_id,
        })


class ConflictError(BaseAppException):
    """Resource conflict error (409)."""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            details=details,
            status_code=409,
            error_type="https://api.example.com/errors/conflict",
        )


class RateLimitError(BaseAppException):
    """Rate limit exceeded error (429)."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
    ) -> None:
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            details=details,
            status_code=429,
            error_type="https://api.example.com/errors/rate-limit",
        )


class FileProcessingError(BaseAppException):
    """File processing error (422)."""
    
    def __init__(
        self,
        message: str = "File processing failed",
        filename: str | None = None,
        file_type: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        error_details = details or {}
        if filename:
            error_details["filename"] = filename
        if file_type:
            error_details["file_type"] = file_type
        
        super().__init__(
            message=message,
            details=error_details,
            status_code=422,
            error_type="https://api.example.com/errors/file-processing",
        )


class ServiceUnavailableError(BaseAppException):
    """Service unavailable error (503)."""
    
    def __init__(
        self,
        service: str = "Service",
        message: str | None = None,
        retry_after: int | None = None,
    ) -> None:
        if message is None:
            message = f"{service} is temporarily unavailable"
        
        details = {"service": service}
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            details=details,
            status_code=503,
            error_type="https://api.example.com/errors/service-unavailable",
        )


class InternalServerError(BaseAppException):
    """Internal server error (500)."""
    
    def __init__(
        self,
        message: str = "Internal server error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            details=details,
            status_code=500,
            error_type="https://api.example.com/errors/internal-server-error",
        )


# Analysis-specific exceptions
class AnalysisError(BaseAppException):
    """Analysis processing error."""
    
    def __init__(
        self,
        message: str = "Analysis failed",
        analysis_type: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        error_details = details or {}
        if analysis_type:
            error_details["analysis_type"] = analysis_type
        
        super().__init__(
            message=message,
            details=error_details,
            status_code=422,
            error_type="https://api.example.com/errors/analysis-error",
        )


class ModelError(BaseAppException):
    """ML model error."""
    
    def __init__(
        self,
        message: str = "Model processing failed",
        model_name: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        error_details = details or {}
        if model_name:
            error_details["model_name"] = model_name
        
        super().__init__(
            message=message,
            details=error_details,
            status_code=500,
            error_type="https://api.example.com/errors/model-error",
        )


# Exception handlers
async def validation_exception_handler(request: Request, exc: ValidationError) -> dict[str, Any]:
    """Handle validation errors."""
    return exc.to_dict()


async def app_exception_handler(request: Request, exc: BaseAppException) -> dict[str, Any]:
    """Handle custom application exceptions."""
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "exception_type": exc.__class__.__name__,
            "status_code": exc.status_code,
            "details": exc.details,
        }
    )
    return exc.to_dict()


async def general_exception_handler(request: Request, exc: Exception) -> dict[str, Any]:
    """Handle unexpected exceptions."""
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "exception_type": exc.__class__.__name__,
        },
        exc_info=True
    )
    
    # Don't expose internal errors in production
    if settings.environment == "production":
        error = InternalServerError()
    else:
        error = InternalServerError(
            message=f"Unexpected error: {str(exc)}",
            details={"exception_type": exc.__class__.__name__}
        )
    
    return error.to_dict()
