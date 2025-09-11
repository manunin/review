"""
Task-based API endpoints for review analysis according to    responses={
        400: {"model": ApiError, "description": "Invalid request"},
        404: {"model": ApiError, "description": "Task not found"},
        422: {"model": ValidationErrorSchema, "description": "Validation Error"},
        500: {"model": ApiError, "description": "Internal server error"}
    }PI specification.
"""
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, File, Form, UploadFile

from ..core.logging import get_logger
from ..infra.db.base import get_db_session, get_session_factory
from ..infra.db.repo import TaskRepository
from .service import TaskService
from .schemas import (
    Task,
    SingleTaskResultRequest,
    BatchTaskResultRequest,
    SingleTaskRequest,
    ApiError,
    ValidationError as ValidationErrorSchema
)

logger = get_logger(__name__)

router = APIRouter(prefix="", tags=["tasks"])


async def get_task_service() -> AsyncGenerator[TaskService, None]:
    """Dependency for task service injection."""
    session_factory = get_session_factory()
    async for session in get_db_session(session_factory):
        task_repo = TaskRepository(session)
        yield TaskService(task_repo)


@router.post(
    "/task/result/single",
    tags=["Task Results"],
    summary="Get last single task result",
    description="Retrieves the result of the last single text analysis task for the user.",
    response_model=Task,
    responses={
        400: {"model": ApiError, "description": "Invalid request"},
        404: {"model": ApiError, "description": "No single task found"},
        422: {"model": ValidationErrorSchema, "description": "Validation Error"},
        500: {"model": ApiError, "description": "Internal server error"}
    }
)
async def get_single_task_result(
    request_data: SingleTaskResultRequest,
    task_service: TaskService = Depends(get_task_service)
) -> Task:
    """Get the last single task result for the user."""
    logger.info("Getting single task result", extra={"request_data": request_data.model_dump()})
    return await task_service.get_last_single_task(request_data.user_id)
    


@router.post(
    "/task/result/batch",
    tags=["Task Results"],
    summary="Get last batch task result",
    description="Retrieves the result of the last batch analysis task for the user.",
    response_model=Task,
    responses={
        400: {"model": ApiError, "description": "Invalid request"},
        404: {"model": ApiError, "description": "No batch task found"},
        422: {"model": ValidationErrorSchema, "description": "Validation Error"},
        500: {"model": ApiError, "description": "Internal server error"}
    }
)
async def get_batch_task_result(
    request_data: BatchTaskResultRequest,
    task_service: TaskService = Depends(get_task_service)
) -> Task:
    """Get the last batch task result for the user."""
    logger.info("Getting batch task result", extra={"request_data": request_data.model_dump()})    
    return await task_service.get_last_batch_task(request_data.user_id)


@router.post(
    "/task/run/single",
    tags=["Task Execution"],
    summary="Send task for analysis single text",
    description="Submits a single text for sentiment analysis.",
    response_model=Task,
    responses={
        400: {"model": ApiError, "description": "Invalid request"},
        422: {"model": ValidationErrorSchema, "description": "Validation error"},
        500: {"model": ApiError, "description": "Internal server error"}
    }
)
async def create_single_task(
    request_data: SingleTaskRequest,
    task_service: TaskService = Depends(get_task_service)
) -> Task:
    """Create a single text analysis task."""
    logger.info("Creating single task", extra={"request_data": request_data.model_dump()})
    task = await task_service.create_single_task(request_data.user_id, request_data.text)
    return task


@router.post(
    "/task/run/batch",
    tags=["Task Execution"],
    summary="Send task for batch (file) analysis",
    description="Submits a file for batch sentiment analysis.",
    response_model=Task,
    responses={
        400: {"model": ApiError, "description": "Invalid request"},
        413: {"model": ApiError, "description": "File too large"},
        415: {"model": ApiError, "description": "Unsupported file format"},
        422: {"model": ValidationErrorSchema, "description": "File processing error"},
        500: {"model": ApiError, "description": "Internal server error"}
    }
)
async def create_batch_task(
    user_id: str = Form(..., description="User identification from cookies"),
    file: UploadFile = File(..., description="File with reviews (CSV/TXT/JSON, max 10MB)"),
    task_service: TaskService = Depends(get_task_service)
) -> Task:
    """Create a batch file analysis task."""
    
    # Validate user_id
    from app.tasks.schemas import validate_user_id
    from app.core.exceptions import ValidationError
    try:
        user_id = validate_user_id(user_id)
    except ValueError as e:
        raise ValidationError(str(e))
    
    logger.info("Creating batch task", extra={"user_id": user_id, "file_name": file.filename})
    file_content = await file.read()
    task = await task_service.create_batch_task(
        user_id=user_id,
        file_content=file_content,
        filename=file.filename or "unknown"
    )
    return task

