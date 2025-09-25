"""
Mock worker for processing tasks in background.
Simulates real task processing workflow.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.db.base import get_session_factory
from app.tasks.models import Task, TaskStatus, TaskType, SentimentEnum

logger = logging.getLogger(__name__)


class MockWorker:
    """Mock worker that processes tasks in background."""
    
    def __init__(self):
        self.session_factory = get_session_factory()
        self.is_running = False
        
    async def start(self):
        """Start the mock worker."""
        logger.info("Starting mock worker...")
        self.is_running = True
        
        while self.is_running:
            try:
                await self._process_pending_tasks()
                await asyncio.sleep(1)  # Check for new tasks every second
            except Exception as e:
                logger.error(f"Error in mock worker: {e}")
                await asyncio.sleep(5)  # Wait longer if there's an error
                
    async def stop(self):
        """Stop the mock worker."""
        logger.info("Stopping mock worker...")
        self.is_running = False
        
    async def _process_pending_tasks(self):
        """Process all pending tasks."""
        async with self.session_factory() as session:
            # Find accepted tasks and move them to queued
            await self._process_accepted_tasks(session)
            
            # Find queued tasks and process them
            await self._process_queued_tasks(session)
            
    async def _process_accepted_tasks(self, session: AsyncSession):
        """Move accepted tasks to queued status."""
        try:
            # Find accepted tasks
            result = await session.execute(
                select(Task).where(Task.status == TaskStatus.accepted)
            )
            accepted_tasks = result.scalars().all()
            
            for task in accepted_tasks:
                logger.info(f"Moving task {task.task_id} from accepted to queued")
                
                # Update status to queued
                await session.execute(
                    update(Task)
                    .where(Task.id == task.id)
                    .values(status=TaskStatus.queued)
                )
                
            if accepted_tasks:
                await session.commit()
                logger.info(f"Moved {len(accepted_tasks)} tasks to queued status")
                
        except Exception as e:
            logger.error(f"Error processing accepted tasks: {e}")
            await session.rollback()
            
    async def _process_queued_tasks(self, session: AsyncSession):
        """Process queued tasks after 5 second delay."""
        try:
            # Find queued tasks that have been queued for at least 5 seconds
            five_seconds_ago = datetime.utcnow() - timedelta(seconds=5)
            
            result = await session.execute(
                select(Task).where(
                    Task.status == TaskStatus.queued,
                    Task.updated_at <= five_seconds_ago
                )
            )
            queued_tasks = result.scalars().all()
            
            for task in queued_tasks:
                logger.info(f"Processing task {task.task_id}")
                
                # Generate mock result based on task type
                if task.type == TaskType.single:
                    await self._process_single_task(session, task)
                elif task.type == TaskType.batch:
                    await self._process_batch_task(session, task)
                    
            if queued_tasks:
                await session.commit()
                logger.info(f"Processed {len(queued_tasks)} tasks to ready status")
                
        except Exception as e:
            logger.error(f"Error processing queued tasks: {e}")
            await session.rollback()
            
    async def _process_single_task(self, session: AsyncSession, task: Task):
        """Process single text analysis task."""
        # Mock sentiment analysis
        mock_sentiment = self._mock_analyze_sentiment(task.text)
        
        # Update task with results
        await session.execute(
            update(Task)
            .where(Task.id == task.id)
            .values(
                status=TaskStatus.ready,
                end=int(time.time()),
                sentiment=mock_sentiment["sentiment"],
                confidence=mock_sentiment["confidence"]
            )
        )
        
    async def _process_batch_task(self, session: AsyncSession, task: Task):
        """Process batch file analysis task."""
        # Mock batch analysis results
        mock_results = self._mock_batch_analysis()
        
        # Update task with results
        await session.execute(
            update(Task)
            .where(Task.id == task.id)
            .values(
                status=TaskStatus.ready,
                end=int(time.time()),
                total_reviews=mock_results["total_reviews"],
                positive=mock_results["positive"],
                negative=mock_results["negative"],
                neutral=mock_results["neutral"],
                positive_percentage=mock_results["positive_percentage"],
                negative_percentage=mock_results["negative_percentage"],
                neutral_percentage=mock_results["neutral_percentage"]
            )
        )
        
    def _mock_analyze_sentiment(self, text: Optional[str]) -> dict:
        """Mock sentiment analysis for single text."""
        if not text:
            return {"sentiment": SentimentEnum.neutral, "confidence": 0.5}
            
        # Simple mock logic based on text content
        text_lower = text.lower()
        
        positive_words = ["хорошо", "отлично", "замечательно", "прекрасно", "рекомендую", "excellent", "great", "amazing", "good", "love"]
        negative_words = ["плохо", "ужасно", "не рекомендую", "bad", "terrible", "awful", "hate", "worst"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return {"sentiment": SentimentEnum.positive, "confidence": 0.85}
        elif negative_count > positive_count:
            return {"sentiment": SentimentEnum.negative, "confidence": 0.80}
        else:
            return {"sentiment": SentimentEnum.neutral, "confidence": 0.60}
            
    def _mock_batch_analysis(self) -> dict:
        """Mock batch analysis results."""
        # Generate random-ish but consistent results
        total = 100
        positive = 65
        negative = 20
        neutral = 15
        
        return {
            "total_reviews": total,
            "positive": positive,
            "negative": negative, 
            "neutral": neutral,
            "positive_percentage": round((positive / total) * 100, 1),
            "negative_percentage": round((negative / total) * 100, 1),
            "neutral_percentage": round((neutral / total) * 100, 1)
        }


# Global worker instance
_worker: Optional[MockWorker] = None


async def get_mock_worker() -> MockWorker:
    """Get the global mock worker instance."""
    global _worker
    if _worker is None:
        _worker = MockWorker()
    return _worker


async def start_mock_worker():
    """Start the global mock worker."""
    worker = await get_mock_worker()
    await worker.start()


async def stop_mock_worker():
    """Stop the global mock worker."""
    global _worker
    if _worker:
        await _worker.stop()
        _worker = None
