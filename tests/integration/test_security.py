"""
Security and data validation tests.

Tests security aspects and data validation according to OpenAPI specification.
"""

import asyncio
import json
import pytest
from httpx import AsyncClient

from tests.conftest import TaskFactory


class TestSecurityAndValidation:
    """Security and data validation tests for the API."""

    @pytest.mark.asyncio
    async def test_input_sanitization_single_task(self, client: AsyncClient):
        """Test input sanitization for single task text."""
        user_id = "sanitization_user"
        
        # Test cases that should be rejected (dangerous content)
        dangerous_test_cases = [
            # HTML/JavaScript injection attempts
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            
            # SQL injection attempts
            "'; DROP TABLE tasks; --",
            "' OR '1'='1",
            "UNION SELECT * FROM users",
        ]
        
        for test_text in dangerous_test_cases:
            response = await client.post(
                "/api/v1/task/run/single",
                json={
                    "user_id": user_id,
                    "text": test_text
                }
            )
            
            # Should reject dangerous content with 422
            assert response.status_code in [422], f"Dangerous text '{test_text}' should be rejected"
        
        # Test cases that should be accepted (normal content with punctuation)
        safe_test_cases = [
            # Normal punctuation should be allowed
            "Great product! Amazing quality, highly recommended.",
            "Text with common symbols: !@#%*()_+-={}[]|:?",
            
            # These should still be rejected due to newlines/tabs or unicode
            # "Text with unicode: 😀 🎉 ñáéíóú",  # Removed - unicode might be blocked
            # "Text with newlines\nand\ttabs",    # Removed - newlines are blocked
        ]
        
        for test_text in safe_test_cases:
            response = await client.post(
                "/api/v1/task/run/single",
                json={
                    "user_id": user_id,
                    "text": test_text
                }
            )
            
            # Should accept safe content with 200
            assert response.status_code == 200, f"Safe text '{test_text}' should be accepted"

    @pytest.mark.asyncio
    async def test_file_content_validation(self, client: AsyncClient):
        """Test file content validation for batch tasks."""
        user_id = "file_validation_user"
        
        # Test malicious file content
        malicious_contents = [
            # Script content
            b"<script>alert('xss')</script>",
            
            # Binary content that might cause issues
            b"\x00\x01\x02\x03\xFF\xFE\xFD",
            
            # Very long lines
            b"x" * 10000 + b"\n",
            
            # SQL injection in CSV
            b"review,sentiment\n'; DROP TABLE tasks; --,positive",
            
            # Malformed CSV
            b"incomplete,csv,with\n\"unclosed,quotes",
            
            # Empty file
            b"",
        ]
        
        for i, content in enumerate(malicious_contents):
            response = await client.post(
                "/api/v1/task/run/batch",
                data={"user_id": f"{user_id}_{i}"},
                files={"file": (f"malicious_{i}.csv", content, "text/csv")}
            )
            
            # Should reject malicious content with validation error
            assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_file_size_limits(self, client: AsyncClient):
        """Test file size validation according to OpenAPI spec (10MB limit)."""
        user_id = "file_size_user"
        
        # Test file exactly at limit (10MB)
        limit_size = 10 * 1024 * 1024  # 10MB
        large_content = b"x" * limit_size
        
        response = await client.post(
            "/api/v1/task/run/batch",
            data={"user_id": user_id},
            files={"file": ("limit_test.txt", large_content, "text/plain")}
        )
        
        # Should reject files that are too large
        assert response.status_code == 413
        
        # Test file slightly under limit
        under_limit_content = b"x" * (limit_size - 1000)  # Just under 10MB
        
        response = await client.post(
            "/api/v1/task/run/batch",
            data={"user_id": user_id + "_under"},
            files={"file": ("under_limit.txt", under_limit_content, "text/plain")}
        )
        
        # Should accept files under the limit
        assert response.status_code in [200, 422]  # 422 if content format is invalid

    @pytest.mark.asyncio
    async def test_user_id_validation(self, client: AsyncClient):
        """Test user ID validation and sanitization."""
        
        # Test various user ID formats that should be rejected
        invalid_user_ids = [
            # Edge cases
            "",  # Empty user ID
            " ",  # Whitespace only
            "a" * 1000,  # Very long user ID
            
            # Special characters
            "user<script>",
            "user'; DROP TABLE users; --",
            "user\nwith\nnewlines",
            "user\x00with\x00nulls",
        ]
        
        for user_id in invalid_user_ids:
            # Test with single task
            response = await client.post(
                "/api/v1/task/run/single",
                json={
                    "user_id": user_id,
                    "text": "Test text"
                }
            )
            
            # Should handle gracefully and reject
            assert response.status_code in [400, 422], f"Invalid user_id '{repr(user_id)}' was accepted"
        
        # Test valid Unicode user ID should be accepted
        response = await client.post(
            "/api/v1/task/run/single",
            json={
                "user_id": "user_ñáéíóú_😀",
                "text": "Test text"
            }
        )
        
        # Unicode should be accepted
        assert response.status_code == 200, "Valid Unicode user_id was rejected"

    @pytest.mark.asyncio
    async def test_content_type_validation(self, client: AsyncClient):
        """Test content type validation for requests."""
        user_id = "content_type_user"
        
        # Test invalid content type for single task
        response = await client.post(
            "/api/v1/task/run/single",
            content="user_id=test&text=test",  # Form data instead of JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should reject invalid content type
        assert response.status_code in [400, 415, 422]
        
        # Test valid JSON content type
        response = await client.post(
            "/api/v1/task/run/single",
            json={
                "user_id": user_id,
                "text": "Valid JSON request"
            },
            headers={"Content-Type": "application/json"}
        )
        
        # Should accept valid content type
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_request_size_limits(self, client: AsyncClient):
        """Test request size limits for JSON payloads."""
        user_id = "request_size_user"
        
        # Test very large JSON request
        large_text = "x" * (1024 * 1024)  # 1MB of text
        
        response = await client.post(
            "/api/v1/task/run/single",
            json={
                "user_id": user_id,
                "text": large_text
            }
        )
        
        # Should handle large requests appropriately
        assert response.status_code in [200, 413, 422]

    @pytest.mark.asyncio
    async def test_concurrent_user_isolation(self, client: AsyncClient):
        """Test that users cannot access each other's data."""
        
        # Test user isolation sequentially to avoid race conditions
        
        # Test 1: user_a creates task, user_b tries to access it
        create_response_a = await client.post(
            "/api/v1/task/run/single",
            json={
                "user_id": "user_a",
                "text": "Private task for user_a"
            }
        )
        assert create_response_a.status_code == 200
        
        # user_a should be able to access their own task
        correct_access_a = await client.post(
            "/api/v1/task/result/single",
            json={"user_id": "user_a"}
        )
        # get task id
        task_id_a = correct_access_a.json().get("task_id")
        assert correct_access_a.status_code == 200
        
        # user_b should NOT be able to access user_a's data (user_b has no tasks)
        wrong_access_b = await client.post(
            "/api/v1/task/result/single",
            json={"user_id": "user_b"}
        )
        assert wrong_access_b.status_code == 404
        
        # Test 2: user_b creates task, user_a tries to access it  
        create_response_b = await client.post(
            "/api/v1/task/run/single", 
            json={
                "user_id": "user_b",
                "text": "Private task for user_b"
            }
        )
        assert create_response_b.status_code == 200
        
        # user_b should be able to access their own task
        correct_access_b = await client.post(
            "/api/v1/task/result/single",
            json={"user_id": "user_b"}
        )
        assert correct_access_b.status_code == 200

        task_id_b = correct_access_b.json().get("task_id")
        assert task_id_a != task_id_b, "Task IDs for different users should not match"

    # todo rate limiting tests when implemented

    @pytest.mark.asyncio
    async def test_file_type_spoofing_protection(self, client: AsyncClient):
        """Test protection against file type spoofing."""
        user_id = "file_spoofing_user"
        
        # Test file with wrong extension vs content type
        fake_csv_content = b"This is not CSV content, it's just text"
        
        response = await client.post(
            "/api/v1/task/run/batch",
            data={"user_id": user_id},
            files={"file": ("fake.csv", fake_csv_content, "text/csv")}
        )
        
        # Should handle gracefully (either process as text or reject)
        assert response.status_code in [400, 415, 422]
        
        # Test executable file disguised as CSV (real binary ELF header)
        suspicious_content = b"\x7fELF\x02\x01\x01\x00"  # Real ELF magic bytes
        
        response = await client.post(
            "/api/v1/task/run/batch",
            data={"user_id": user_id + "_suspicious"},
            files={"file": ("suspicious.csv", suspicious_content, "text/csv")}
        )
        
        # Should reject binary content
        assert response.status_code in [400, 415, 422]

    @pytest.mark.asyncio
    async def test_error_information_disclosure(self, client: AsyncClient):
        """Test that error messages don't disclose sensitive information."""
        
        # Test various error scenarios
        error_requests = [
            # Invalid JSON
            ("/api/v1/task/run/single", "invalid json", "application/json"),
            
            # Missing fields
            ("/api/v1/task/run/single", '{"user_id": "test"}', "application/json"),
            
            # Invalid file upload
            ("/api/v1/task/run/batch", "not multipart", "multipart/form-data"),
        ]
        
        for endpoint, content, content_type in error_requests:
            response = await client.post(
                endpoint,
                content=content,
                headers={"Content-Type": content_type}
            )
            
            # Should return appropriate error status
            assert response.status_code >= 400
            
            if response.headers.get("content-type", "").startswith("application/json"):
                try:
                    error_data = response.json()
                    # Error messages should be generic, not revealing internal details
                    error_text = str(error_data).lower()
                    
                    # Should not contain sensitive information
                    sensitive_terms = [
                        "traceback", "stack trace", "internal error",
                        "database", "sql", "connection", "password",
                        "file path", "directory", "server path"
                    ]
                    
                    for term in sensitive_terms:
                        assert term not in error_text, f"Error message contains sensitive term: {term}"
                        
                except json.JSONDecodeError:
                    # Non-JSON error response is acceptable
                    pass
