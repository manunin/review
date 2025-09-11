"""
Custom exceptions and error handling following RFC 7807 Problem Details format.
"""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

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
        """Convert exception to OpenAPI-compliant format."""
        error_response = {
            "message": self.message,
        }
        
        if self.details:
            error_response["details"] = self.details
        
        return error_response


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


# Exception handlers
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle validation errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "exception_type": exc.__class__.__name__,
            "status_code": exc.status_code,
            "details": exc.details,
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
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
    
    return JSONResponse(
        status_code=error.status_code,
        content=error.to_dict()
    )
