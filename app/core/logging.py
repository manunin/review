"""
Structured JSON logging with correlation ID support.
"""

from __future__ import annotations

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

from pythonjsonlogger import jsonlogger

# Context variable for request correlation ID
request_id_context: ContextVar[str] = ContextVar("request_id", default="")


class CorrelationFilter(logging.Filter):
    """Add correlation ID to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get("")
        return True


class SecretMaskingFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with secret masking."""
    
    SENSITIVE_FIELDS = {
        "password", "token", "key", "secret", "auth", "credential",
        "jwt", "bearer", "authorization", "x-api-key"
    }
    
    def process_log_record(self, log_record: dict[str, Any]) -> dict[str, Any]:
        """Process log record and mask sensitive information."""
        # Mask sensitive fields
        for key, value in log_record.items():
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                if isinstance(value, str) and len(value) > 8:
                    log_record[key] = f"{value[:4]}***{value[-4:]}"
                else:
                    log_record[key] = "***masked***"
        
        return log_record


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured JSON logging."""
    
    # Create custom formatter
    formatter = SecretMaskingFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(request_id)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        json_ensure_ascii=False
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(CorrelationFilter())
    
    root_logger.addHandler(console_handler)
    
    # Set library log levels to avoid spam
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get logger with correlation support."""
    return logging.getLogger(name)


def set_request_id(request_id: str | None = None) -> str:
    """Set request ID in context. Generate if not provided."""
    if not request_id:
        request_id = str(uuid.uuid4())
    
    request_id_context.set(request_id)
    return request_id


def get_request_id() -> str:
    """Get current request ID from context."""
    return request_id_context.get("")


def mask_sensitive_data(data: dict[str, Any]) -> dict[str, Any]:
    """
    Mask sensitive data in dictionaries for logging.
    
    Usage example:
        user_data = {"name": "John", "password": "secret123", "email": "john@example.com"}
        safe_data = mask_sensitive_data(user_data)
        logger.info("User data processed", extra={"user": safe_data})
    """
    masked_data = data.copy()
    
    sensitive_fields = {
        "password", "token", "key", "secret", "auth", "credential",
        "jwt", "bearer", "authorization", "x-api-key"
    }
    
    for key, value in masked_data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            if isinstance(value, str) and len(value) > 8:
                masked_data[key] = f"{value[:4]}***{value[-4:]}"
            else:
                masked_data[key] = "***masked***"
    
    return masked_data
