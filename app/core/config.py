"""
Configuration settings for the Smart Review Analyzer application.
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/review_db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Model paths
    MODEL_PATH: str = "models/sentiment_model.pkl"
    VECTORIZER_PATH: str = "models/vectorizer.pkl"
    
    # File upload settings
    MAX_FILE_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".txt", ".csv", ".json", ".xlsx"]
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Development
    DEBUG: bool = True
    RELOAD: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
