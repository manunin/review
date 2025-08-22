"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis

from app.core.config import settings

# SQLAlchemy database engine
engine = create_engine(settings.DATABASE_URL)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

# Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis():
    """Dependency to get Redis client."""
    return redis_client
