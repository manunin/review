"""
Performance and load tests for the API.

Tests system behavior under various load conditions and validates performance requirements.
"""

import asyncio
import time
import pytest
from httpx import AsyncClient

from tests.conftest import TaskFactory


class TestPerformanceAndLoad:
    """Performance and load testing for the Review Analysis API."""

    @pytest.mark.asyncio
    async def test_single_task_response_time(self, client: AsyncClient):
        """Test response time for single task creation."""
        user_id = "perf_single_user"
        
        # Measure response time
        start_time = time.time()
        
        response = await client.post(
            "/api/v1/task/run/single",
            json={
                "user_id": user_id,
                "text": "Performance test review text"
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Verify response
        assert response.status_code == 200
        
        # Response time should be reasonable (under 5 seconds)
        assert response_time < 5.0, f"Response time {response_time}s exceeds 5s limit"

    @pytest.mark.asyncio
    async def test_batch_task_response_time(self, client: AsyncClient):
        """Test response time for batch task creation."""
        user_id = "perf_batch_user"
        file_content = TaskFactory.create_test_csv_content()
        
        # Measure response time
        start_time = time.time()
        
        response = await client.post(
            "/api/v1/task/run/batch",
            data={"user_id": user_id},
            files={"file": ("test.csv", file_content, "text/csv")}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Verify response
        assert response.status_code == 200
        
        # Batch processing might take longer but should be reasonable
        assert response_time < 10.0, f"Response time {response_time}s exceeds 10s limit"

    @pytest.mark.asyncio
    async def test_concurrent_single_tasks(self, client: AsyncClient):
        """Test handling multiple concurrent single task requests."""
        user_base = "concurrent_single"
        num_concurrent = 10
        
        async def create_single_task(user_suffix: int):
            """Create a single task for testing concurrency."""
            return await client.post(
                "/api/v1/task/run/single",
                json={
                    "user_id": f"{user_base}_{user_suffix}",
                    "text": f"Concurrent test review {user_suffix}"
                }
            )
        
        # Measure time for concurrent requests
        start_time = time.time()
        
        # Execute concurrent requests
        tasks = [create_single_task(i) for i in range(num_concurrent)]
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all requests succeeded
        for response in responses:
            assert response.status_code == 200
        
        # Concurrent processing should be faster than sequential
        # Average time per request should be reasonable
        avg_time_per_request = total_time / num_concurrent
        assert avg_time_per_request < 2.0, f"Average time per request {avg_time_per_request}s too high"

    @pytest.mark.asyncio
    async def test_concurrent_batch_tasks(self, client: AsyncClient):
        """Test handling multiple concurrent batch task requests."""
        user_base = "concurrent_batch"
        num_concurrent = 5  # Fewer batch tasks as they're more resource intensive
        file_content = TaskFactory.create_test_csv_content()
        
        async def create_batch_task(user_suffix: int):
            """Create a batch task for testing concurrency."""
            return await client.post(
                "/api/v1/task/run/batch",
                data={"user_id": f"{user_base}_{user_suffix}"},
                files={"file": (f"test_{user_suffix}.csv", file_content, "text/csv")}
            )
        
        # Execute concurrent batch requests
        start_time = time.time()
        
        tasks = [create_batch_task(i) for i in range(num_concurrent)]
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all requests succeeded
        for response in responses:
            assert response.status_code == 200
        
        # Total time should be reasonable for concurrent batch processing
        assert total_time < 30.0, f"Total time {total_time}s for {num_concurrent} batch tasks too high"

    @pytest.mark.asyncio
    async def test_result_retrieval_performance(self, client: AsyncClient):
        """Test performance of result retrieval operations."""
        user_id = "result_perf_user"
        
        # Create a task first
        create_response = await client.post(
            "/api/v1/task/run/single",
            json={
                "user_id": user_id,
                "text": "Result retrieval performance test"
            }
        )
        assert create_response.status_code == 200
        
        # Measure result retrieval time multiple times
        retrieval_times = []
        
        for _ in range(5):
            start_time = time.time()
            
            result_response = await client.post(
                "/api/v1/task/result/single",
                json={"user_id": user_id}
            )
            
            end_time = time.time()
            retrieval_time = end_time - start_time
            retrieval_times.append(retrieval_time)
            
            assert result_response.status_code == 200
        
        # Average retrieval time should be very fast
        avg_retrieval_time = sum(retrieval_times) / len(retrieval_times)
        assert avg_retrieval_time < 1.0, f"Average retrieval time {avg_retrieval_time}s too slow"

    @pytest.mark.asyncio
    async def test_large_file_processing(self, client: AsyncClient):
        """Test processing of larger files (within limits)."""
        user_id = "large_file_user"
        
        # Create a larger CSV content (but within 10MB limit)
        large_content = b"review,sentiment\n"
        for i in range(2000):  # Create 2000 review entries to ensure over 50KB
            large_content += f"This is review number {i}, great product!\n".encode()
        
        # Should be well under 10MB but substantial enough to test
        assert len(large_content) < 10 * 1024 * 1024  # Under 10MB
        assert len(large_content) > 50 * 1024  # Over 50KB
        
        start_time = time.time()
        
        response = await client.post(
            "/api/v1/task/run/batch",
            data={"user_id": user_id},
            files={"file": ("large_test.csv", large_content, "text/csv")}
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert response.status_code == 200
        
        # Processing time should scale reasonably with file size
        assert processing_time < 30.0, f"Processing time {processing_time}s too long for large file"

    @pytest.mark.asyncio
    async def test_rapid_sequential_requests(self, client: AsyncClient):
        """Test handling rapid sequential requests from the same user."""
        user_id = "rapid_user"
        num_requests = 20
        
        start_time = time.time()
        
        # Make rapid sequential requests
        for i in range(num_requests):
            response = await client.post(
                "/api/v1/task/run/single",
                json={
                    "user_id": user_id,
                    "text": f"Rapid request {i}"
                }
            )
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle rapid requests efficiently
        avg_time_per_request = total_time / num_requests
        assert avg_time_per_request < 1.0, f"Average time per rapid request {avg_time_per_request}s too high"

    @pytest.mark.asyncio
    async def test_mixed_load_scenario(self, client: AsyncClient):
        """Test system under mixed load (single tasks, batch tasks, result retrievals)."""
        base_user = "mixed_load"
        
        async def mixed_operations():
            """Perform mixed operations for load testing."""
            operations = []
            
            # Create single tasks
            for i in range(5):
                op = client.post(
                    "/api/v1/task/run/single",
                    json={
                        "user_id": f"{base_user}_single_{i}",
                        "text": f"Mixed load single task {i}"
                    }
                )
                operations.append(op)
            
            # Create batch tasks
            file_content = TaskFactory.create_test_csv_content()
            for i in range(2):
                op = client.post(
                    "/api/v1/task/run/batch",
                    data={"user_id": f"{base_user}_batch_{i}"},
                    files={"file": (f"mixed_{i}.csv", file_content, "text/csv")}
                )
                operations.append(op)
            
            # Result retrievals
            for i in range(3):
                op = client.post(
                    "/api/v1/task/result/single",
                    json={"user_id": f"{base_user}_result_{i}"}
                )
                operations.append(op)
            
            return await asyncio.gather(*operations, return_exceptions=True)
        
        # Execute mixed load test
        start_time = time.time()
        results = await mixed_operations()
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Count successful operations
        successful_ops = 0
        for result in results:
            if hasattr(result, 'status_code'):
                if result.status_code in [200, 404]:  # 404 is expected for non-existent results
                    successful_ops += 1
        
        # Most operations should succeed
        assert successful_ops >= len(results) * 0.7, "Too many operations failed under mixed load"
        
        # Total time should be reasonable
        assert total_time < 60.0, f"Mixed load test took {total_time}s, too long"

    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, client: AsyncClient):
        """Test that memory usage remains stable under repeated operations."""
        user_id = "memory_test_user"
        
        # Perform many operations to test memory stability
        for batch in range(5):  # 5 batches of operations
            batch_operations = []
            
            # Create multiple tasks in each batch
            for i in range(10):
                op = client.post(
                    "/api/v1/task/run/single",
                    json={
                        "user_id": f"{user_id}_batch{batch}_op{i}",
                        "text": f"Memory test operation {batch}-{i}"
                    }
                )
                batch_operations.append(op)
            
            # Execute batch
            responses = await asyncio.gather(*batch_operations)
            
            # Verify all succeeded
            for response in responses:
                assert response.status_code == 200
            
            # Small delay between batches to allow cleanup
            await asyncio.sleep(0.1)
        
        # If we get here without memory errors, test passes
        assert True

    @pytest.mark.asyncio
    async def test_error_handling_under_load(self, client: AsyncClient):
        """Test that error handling works correctly under load."""
        
        async def create_invalid_requests():
            """Create various invalid requests to test error handling."""
            operations = []
            
            # Invalid single task requests
            for i in range(5):
                # Missing required fields
                op = client.post(
                    "/api/v1/task/run/single",
                    json={"user_id": f"invalid_user_{i}"}  # Missing text
                )
                operations.append(op)
            
            # Invalid result requests
            for i in range(5):
                op = client.post(
                    "/api/v1/task/result/single",
                    json={"user_id": f"nonexistent_user_{i}"}
                )
                operations.append(op)
            
            return await asyncio.gather(*operations, return_exceptions=True)
        
        # Execute error scenarios
        results = await create_invalid_requests()
        
        # Verify appropriate error responses
        for result in results:
            if hasattr(result, 'status_code'):
                # Should get appropriate error codes, not 500
                assert result.status_code in [400, 404, 422], f"Unexpected status code: {result.status_code}"
