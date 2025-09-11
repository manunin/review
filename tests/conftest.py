"""
Test configuration and fixtures.
"""

import asyncio
import os
import uuid
from typing import AsyncGenerator

import pytest
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.infra.db.base import Base, get_session_factory, init_db
from app.tasks.models import Task as DbTask, TaskStatus, TaskType
from app.tasks.service import TaskService
from app.infra.db.repo import TaskRepository


@pytest.fixture(scope="session")
def postgres_container():
    """Create PostgreSQL container for testing."""
    container = PostgresContainer("postgres:15")
    container.start()
    yield container
    container.stop()


@pytest.fixture(scope="session")
def test_database_url(postgres_container):
    """Get test database URL from container."""
    connection_url = postgres_container.get_connection_url()
    # Replace both postgresql:// and psycopg2 driver with asyncpg
    async_url = connection_url.replace("postgresql://", "postgresql+asyncpg://")
    async_url = async_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    return async_url


@pytest.fixture
async def db_engine(test_database_url):
    """Create test database engine."""
    engine = create_async_engine(test_database_url, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for testing."""
    from sqlalchemy.ext.asyncio import async_sessionmaker
    
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
async def task_repository(db_session: AsyncSession) -> TaskRepository:
    """Create task repository for testing."""
    return TaskRepository(db_session)


@pytest.fixture
async def task_service(task_repository: TaskRepository) -> TaskService:
    """Create task service for testing."""
    return TaskService(task_repository)


@pytest.fixture
async def app(test_database_url):
    """Create FastAPI application for testing."""
    # Set test database URL in environment
    os.environ["DATABASE_URL"] = test_database_url
    
    # Initialize database
    await init_db(test_database_url)
    
    # Create tables
    from app.infra.db.base import get_engine
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Import app instance
    from app.main import app
    return app


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        yield client


# Test data factories
class TaskFactory:
    """Factory for creating test task data."""
    
    @staticmethod
    def create_single_task_request(user_id: str = "test_user", text: str = "Great product!"):
        """Create single task request data."""
        return {
            "user_id": user_id,
            "text": text
        }
    
    @staticmethod
    def create_user_request(user_id: str = "test_user"):
        """Create user request data."""
        return {
            "user_id": user_id
        }
    
    @staticmethod
    def create_test_csv_content():
        """Create test CSV content for batch analysis."""
        return b"review,sentiment\nGreat product!,positive\nTerrible quality,negative\nOkay product,neutral"
    
    @staticmethod
    def create_test_txt_content():
        """Create test TXT content for batch analysis."""
        return b"Great product!\nTerrible quality\nOkay product"
    
    @staticmethod
    def create_test_json_content():
        """Create test JSON content for batch analysis."""
        return b'[{"review": "Great product!"}, {"review": "Terrible quality"}, {"review": "Okay product"}]'
