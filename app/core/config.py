"""
Core configuration module using pydantic-settings.
Handles environment variables and application settings.
"""

from __future__ import annotations

import os
from typing import List, Literal, Optional, Union

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8", 
        "case_sensitive": False,
        "protected_namespaces": ("settings_",),
        "extra": "ignore"  # Ignore extra fields from .env
    }
    
    # Application
    app_name: str = "Review Analysis API"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/review_db",
        description="PostgreSQL connection URL"
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    
    # Redis (Task Queue)
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for task queue"
    )
    
    # File Upload
    max_file_size_mb: int = 10
    max_text_length: int = 512
    temp_dir: str = "/tmp/review_uploads"
    file_cleanup_hours: int = 24
    # Note: allowed_extensions simplified to avoid env parsing issues
    
    @property
    def allowed_extensions(self) -> List[str]:
        """Get allowed file extensions."""
        return [".txt", ".csv", ".json"]
    
    # Task Processing
    task_timeout_minutes: int = 30
    max_concurrent_tasks: int = 100
    task_retry_attempts: int = 3
    
    # ML Model
    model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    model_cache_dir: str = "./models"
    batch_size: int = 32
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT and other crypto operations")
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 30
    
    # CORS - simplified to avoid env parsing issues
    cors_allow_credentials: bool = True
    
    @property  
    def cors_origins(self) -> List[str]:
        """Get CORS origins."""
        return ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @property
    def cors_allow_methods(self) -> List[str]:
        """Get allowed CORS methods."""
        return ["GET", "POST", "OPTIONS"]
    
    @property
    def cors_allow_headers(self) -> List[str]:
        """Get allowed CORS headers."""
        return ["*"]
    
    # Observability
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    enable_request_logging: bool = True
    enable_metrics: bool = True
    
    # API Documentation
    show_docs: bool = True
    openapi_url: Optional[str] = "/openapi.json"
    docs_url: Optional[str] = "/docs"
    redoc_url: Optional[str] = "/redoc"
    
    @validator("show_docs", pre=True, always=True)
    def validate_docs_visibility(cls, v, values):
        """Hide docs in production unless explicitly enabled."""
        if values.get("environment") == "production" and v is True:
            # In production, explicitly check if docs should be shown
            return os.getenv("FORCE_SHOW_DOCS", "false").lower() == "true"
        return v
    
    @validator("openapi_url", "docs_url", "redoc_url", pre=True, always=True)
    def validate_docs_urls(cls, v, values):
        """Set docs URLs to None if docs are disabled."""
        if not values.get("show_docs", True):
            return None
        return v
    
    @validator("max_file_size_mb")
    def validate_file_size(cls, v):
        """Ensure file size is reasonable."""
        if v <= 0 or v > 100:
            raise ValueError("File size must be between 1 and 100 MB")
        return v
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes for file validation."""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


# Global settings instance
settings = Settings()
