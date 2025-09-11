"""
Security utilities and middleware for the application.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import get_logger, set_request_id

logger = get_logger(__name__)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracking and correlation ID management."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Extract or generate request ID
        request_id = (
            request.headers.get("X-Request-ID") or
            request.headers.get("X-Correlation-ID") or
            str(uuid.uuid4())
        )
        
        # Set request ID in context
        set_request_id(request_id)
        
        # Log incoming request
        if settings.enable_request_logging:
            logger.info(
                "Incoming request",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        # Log response
        if settings.enable_request_logging:
            logger.info(
                "Request completed",
                extra={
                    "status_code": response.status_code,
                    "response_time_ms": getattr(request.state, "response_time", 0),
                }
            )
        
        return response


class SanitizationMiddleware(BaseHTTPMiddleware):
    """Middleware for sanitizing incoming request data."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Only sanitize JSON body for POST requests
        if request.method == "POST" and "application/json" in request.headers.get("content-type", ""):
            body = await request.body()
            if body:
                import json
                try:
                    data = json.loads(body)
                    if isinstance(data, dict):
                        sanitized_data = {k: sanitize_text(v) if isinstance(v, str) else v for k, v in data.items()}
                        request._body = json.dumps(sanitized_data).encode('utf-8')
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # If parsing fails, continue without sanitization
                    raise HTTPException(status_code=422, detail="Invalid JSON")

        response = await call_next(request)
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
        })
        
        return response


def setup_cors(app) -> None:
    """Configure CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        expose_headers=["X-Request-ID"],
    )


async def extract_user_id_from_request(request: Request) -> str:
    """
    Extract user ID from request.
    
    In this implementation, we use a simple approach:
    1. Check for user_id in request body (for POST requests)
    2. Generate a session-based ID from client info
    3. Could be extended to use proper authentication
    """
    # Step 1: Check for user_id in request body (for POST requests)
    if request.method == "POST":
        try:
            body = await request.body()
            if body:
                # Try to parse JSON body
                import json
                try:
                    body_data = json.loads(body.decode())
                    if isinstance(body_data, dict) and "user_id" in body_data:
                        return str(body_data["user_id"])
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # If parsing fails, continue to fallback
                    pass
        except Exception:
            # If body reading fails, continue to fallback
            pass
    
    # Step 2: Check for user_id in headers
    user_id_header = request.headers.get("X-User-ID") or request.headers.get("User-ID")
    if user_id_header:
        return user_id_header
    
    # Step 3: Generate a session-based ID from client info (fallback)
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Generate a consistent ID based on client info
    # In production, this should be replaced with proper user authentication
    session_id = f"session_{client_ip}_{hash(user_agent) % 10000}"
    
    return session_id


def validate_file_type(filename: str) -> bool:
    """Validate if file type is allowed."""
    if not filename:
        return False
    
    # Check extension
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    return f".{file_ext}" in settings.allowed_extensions


def validate_file_size(file_size: int) -> bool:
    """Validate if file size is within limits."""
    return 0 < file_size <= settings.max_file_size_mb * 1024 * 1024


def sanitize_text(text: str) -> str:
    """Sanitize input text for analysis."""
    if not text:
        return ""
    
    # Basic sanitization
    sanitized = text.strip()
    
    # Remove potential XSS patterns (basic protection)
    dangerous_patterns = ["<script", "</script", "javascript:", "onclick", "onerror"]
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern, "")
    
    return sanitized


def create_api_error(
    message: str,
    details: dict[str, Any] | None = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> HTTPException:
    """Create standardized API error response."""
    error_content = {"message": message}
    if details:
        error_content["details"] = details
    
    return HTTPException(status_code=status_code, detail=error_content)
