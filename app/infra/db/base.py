"""
Database engine and session factory with async SQLAlchemy setup.

This module provides:
- Async SQLAlchemy engine configuration
- Session factory for dependency injection
- Connection pooling configuration
- Lifespan management for DB connections
"""

from typing import AsyncGenerator, Optional, Tuple
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings


# Database naming conventions following PostgreSQL standards
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    
    metadata = metadata


async def create_engine_session(database_url: str) -> Tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """
    Create async database engine and session factory.
    
    Args:
        database_url: Database connection URL
        
    Returns:
        Tuple of (engine, session_factory)
    """
    
    # Engine configuration with connection pooling
    engine_kwargs = {
        "echo": settings.database_echo,
        "future": True,
    }
    
    # Use NullPool for SQLite (testing), connection pool for PostgreSQL
    if database_url.startswith("sqlite"):
        engine_kwargs["poolclass"] = NullPool
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        # PostgreSQL connection pool settings
        engine_kwargs.update({
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # 1 hour
        })
    
    engine = create_async_engine(database_url, **engine_kwargs)
    
    # Session factory
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    
    return engine, session_factory


async def get_db_session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency for FastAPI.
    
    Args:
        session_factory: Async session factory
        
    Yields:
        Database session
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Global variables for application state
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


async def init_db(database_url: str) -> None:
    """
    Initialize database engine and session factory.
    
    Args:
        database_url: Database connection URL
    """
    global _engine, _session_factory
    
    _engine, _session_factory = await create_engine_session(database_url)


async def close_db() -> None:
    """Close database engine and cleanup resources."""
    global _engine, _session_factory
    
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Get current session factory.
    
    Returns:
        Session factory instance
        
    Raises:
        RuntimeError: If database is not initialized
    """
    if _session_factory is None:
        raise RuntimeError("Database is not initialized. Call init_db() first.")
    
    return _session_factory


def get_engine() -> AsyncEngine:
    """
    Get current database engine.
    
    Returns:
        Database engine instance
        
    Raises:
        RuntimeError: If database is not initialized
    """
    if _engine is None:
        raise RuntimeError("Database is not initialized. Call init_db() first.")
    
    return _engine
