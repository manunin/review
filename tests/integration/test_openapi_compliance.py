"""
Integration tests for OpenAPI specification compliance.

Tests that our API implementation matches exactly the specification in api/openapi.yml.
"""

import json
import pytest
from httpx import AsyncClient

from tests.conftest import TaskFactory


class TestOpenAPICompliance:
    """Test API endpoints according to OpenAPI specification."""

    @pytest.mark.asyncio
    async def test_single_task_creation_and_result(self, client: AsyncClient):
        """Test POST /task/run/single and POST /task/result/single endpoints."""
        
        # Test data according to OpenAPI spec
        user_id = "test_user_123"
        text = "Great product, highly recommended!"
        
        # Create single analysis task
        create_response = await client.post(
            "/api/v1/task/run/single",
            json={
                "user_id": user_id,
                "text": text
            }
        )
        
        # Verify task creation response
        assert create_response.status_code == 200
        create_data = create_response.json()
        
        # Validate response structure according to OpenAPI
        assert "task_id" in create_data
        task_id = create_data["task_id"]
        assert "type" in create_data
        assert "status" in create_data
        assert "start" in create_data
        
        assert create_data["type"] == "single"
        assert create_data["status"] in ["accepted", "queued", "ready"]
        assert isinstance(create_data["start"], int)
        
        # If task is ready immediately, check result structure
        if create_data["status"] == "ready":
            assert "result" in create_data
            result = create_data["result"]
            assert "sentiment" in result
            assert "confidence" in result
            assert result["sentiment"] in ["positive", "negative", "neutral"]
            assert 0.0 <= result["confidence"] <= 1.0
        
        # Get task result
        result_response = await client.post(
            "/api/v1/task/result/single",
            json={"user_id": user_id}
        )
        
        # Verify result response
        assert result_response.status_code == 200
        result_data = result_response.json()
        
        # Validate result structure
        assert "task_id" in result_data
        assert result_data["task_id"] == task_id
        assert "type" in result_data
        assert "status" in result_data
        assert "start" in result_data
        
        assert result_data["type"] == "single"
        assert result_data["status"] in ["accepted", "queued", "ready", "error"]
        
        # If task is completed, validate result
        if result_data["status"] == "ready":
            assert "result" in result_data
            result = result_data["result"]
            assert "sentiment" in result
            assert "confidence" in result
            assert result["sentiment"] in ["positive", "negative", "neutral"]
            assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_batch_task_creation_and_result(self, client: AsyncClient):
        """Test POST /task/run/batch and POST /task/result/batch endpoints."""
        
        user_id = "batch_user_456"
        
        # Create test file content
        test_file_content = TaskFactory.create_test_csv_content()
        
        # Create batch analysis task with multipart/form-data
        create_response = await client.post(
            "/api/v1/task/run/batch",
            data={"user_id": user_id},
            files={"file": ("test_reviews.csv", test_file_content, "text/csv")}
        )
        
        # Verify task creation response
        assert create_response.status_code == 200
        create_data = create_response.json()
        
        # Validate response structure
        assert "task_id" in create_data
        task_id = create_data["task_id"]
        assert "type" in create_data
        assert "status" in create_data
        assert "start" in create_data
        
        assert create_data["type"] == "batch"
        assert create_data["status"] in ["accepted", "queued", "ready"]

        # Get task result
        result_response = await client.post(
            "/api/v1/task/result/batch",
            json={"user_id": user_id}
        )
        
        # Verify result response
        assert result_response.status_code == 200
        result_data = result_response.json()

        assert "task_id" in result_data
        assert result_data["task_id"] == task_id

        # Validate batch result structure
        assert result_data["type"] == "batch"

        if result_data["status"] == "ready":
            assert "result" in result_data
            result = result_data["result"]
            
            # Validate batch result fields according to OpenAPI
            required_fields = [
                "total_reviews", "positive", "negative", "neutral",
                "positive_percentage", "negative_percentage", "neutral_percentage"
            ]
            for field in required_fields:
                assert field in result
                assert isinstance(result[field], (int, float))
            
            # Validate ranges
            assert result["total_reviews"] >= 0
            assert result["positive"] >= 0
            assert result["negative"] >= 0
            assert result["neutral"] >= 0
            assert 0.0 <= result["positive_percentage"] <= 100.0
            assert 0.0 <= result["negative_percentage"] <= 100.0
            assert 0.0 <= result["neutral_percentage"] <= 100.0

    @pytest.mark.asyncio
    async def test_single_task_validation_errors(self, client: AsyncClient):
        """Test validation errors for single task endpoint."""
        
        # Test missing user_id
        response = await client.post(
            "/api/v1/task/run/single",
            json={"text": "Some text"}
        )
        assert response.status_code == 422
        
        # Test missing text
        response = await client.post(
            "/api/v1/task/run/single",
            json={"user_id": "test_user"}
        )
        assert response.status_code == 422
        
        # Test text too long (over 512 characters)
        long_text = "x" * 513
        response = await client.post(
            "/api/v1/task/run/single",
            json={
                "user_id": "test_user",
                "text": long_text
            }
        )
        assert response.status_code == 422
        

    @pytest.mark.asyncio
    async def test_batch_task_validation_errors(self, client: AsyncClient):
        """Test validation errors for batch task endpoint."""
        
        # Test file too large
        large_file_content = b"x" * (11 * 1024 * 1024)  # 11MB, exceeds 10MB limit
        
        response = await client.post(
            "/api/v1/task/run/batch",
            data={"user_id": "test_user"},
            files={"file": ("large_file.txt", large_file_content, "text/plain")}
        )
        assert response.status_code == 413
        assert response.json()["message"] == "File size exceeds the maximum limit of 10MB."
        
        # Test missing user_id
        response = await client.post(
            "/api/v1/task/run/batch",
            files={"file": ("test.csv", b"test,data", "text/csv")}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_no_task_found_responses(self, client: AsyncClient):
        """Test 404 responses when no tasks found."""
        
        # Test single task not found
        response = await client.post(
            "/api/v1/task/result/single",
            json={"user_id": "nonexistent_user"}
        )
        assert response.status_code == 404
        response_data = response.json()
        print("DEBUG: No single task found response", response_data)
        assert "message" in response_data
        assert "No single task found" in response_data["message"]
        
        # Test batch task not found
        response = await client.post(
            "/api/v1/task/result/batch",
            json={"user_id": "nonexistent_user"}
        )
        assert response.status_code == 404
        response_data = response.json()
        assert "message" in response_data
        assert "No batch task found" in response_data["message"]

    @pytest.mark.asyncio
    async def test_response_format_compliance(self, client: AsyncClient):
        """Test that response formats match OpenAPI spec exactly."""
        
        # Create a task and verify all field types and structures
        user_id = "format_test_user"
        
        response = await client.post(
            "/api/v1/task/run/single",
            json={
                "user_id": user_id,
                "text": "Test text for format validation"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify UUID format for task_id
        import uuid
        try:
            uuid.UUID(data["task_id"])
        except ValueError:
            pytest.fail(f"task_id '{data['task_id']}' is not a valid UUID")
        
        # Verify enum values
        assert data["type"] in ["single", "batch"]
        assert data["status"] in ["accepted", "queued", "ready", "error"]
        
        # Verify timestamp is integer
        assert isinstance(data["start"], int)
        
        # If task has result, verify result structure
        if "result" in data and data["result"]:
            result = data["result"]
            if "sentiment" in result:
                assert result["sentiment"] in ["positive", "negative", "neutral"]
            if "confidence" in result:
                assert isinstance(result["confidence"], (int, float))
                assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_file_format_support(self, client: AsyncClient):
        """Test supported file formats for batch analysis."""
        
        user_id = "file_test_user"
        
        # Test CSV file
        csv_content = TaskFactory.create_test_csv_content()
        response = await client.post(
            "/api/v1/task/run/batch",
            data={"user_id": user_id},
            files={"file": ("test.csv", csv_content, "text/csv")}
        )
        assert response.status_code == 200
        
        # Test TXT file
        txt_content = TaskFactory.create_test_txt_content()
        response = await client.post(
            "/api/v1/task/run/batch",
            data={"user_id": user_id + "_txt"},
            files={"file": ("test.txt", txt_content, "text/plain")}
        )
        assert response.status_code == 200
        
        # Test JSON file
        json_content = TaskFactory.create_test_json_content()
        response = await client.post(
            "/api/v1/task/run/batch",
            data={"user_id": user_id + "_json"},
            files={"file": ("test.json", json_content, "application/json")}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_unsupported_file_format(self, client: AsyncClient):
        """Test error response for unsupported file formats."""
        
        user_id = "unsupported_test_user"
        
        # Test unsupported file format
        response = await client.post(
            "/api/v1/task/run/batch",
            data={"user_id": user_id},
            files={"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        )
        assert response.status_code == 415
        response_data = response.json()
        assert "message" in response_data
        assert "Unsupported file format" in response_data["message"]

    @pytest.mark.asyncio
    async def test_error_responses_structure(self, client: AsyncClient):
        """Test that error responses match OpenAPI specification."""
        
        # Test validation error structure
        response = await client.post(
            "/api/v1/task/run/single",
            json={}  # Missing required fields
        )
        assert response.status_code == 422
        error_data = response.json()
        
        # Should have message field according to ValidationError schema
        assert "message" in error_data or "detail" in error_data
        
        # Test 404 error structure
        response = await client.post(
            "/api/v1/task/result/single",
            json={"user_id": "nonexistent"}
        )
        assert response.status_code == 404
        error_data = response.json()
        assert "message" in error_data

    @pytest.mark.asyncio
    async def test_concurrent_tasks_same_user(self, client: AsyncClient):
        """Test handling multiple tasks for the same user."""
        
        user_id = "concurrent_test_user"
        
        # Create multiple single tasks
        tasks = []
        for i in range(3):
            response = await client.post(
                "/api/v1/task/run/single",
                json={
                    "user_id": user_id,
                    "text": f"Test text {i}"
                }
            )
            assert response.status_code == 200
            tasks.append(response.json())
        
        # Get result should return the latest task
        result_response = await client.post(
            "/api/v1/task/result/single",
            json={"user_id": user_id}
        )
        assert result_response.status_code == 200
        result_data = result_response.json()
        
        # Verify we get a valid task result
        assert "task_id" in result_data
        assert "type" in result_data
        assert result_data["type"] == "single"

        # Get last task result by created_at field
        last_task = max(tasks, key=lambda x: x["start"])
        assert last_task["task_id"] == result_data["task_id"]
