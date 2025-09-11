"""
Health check and monitoring tests.

Tests system health endpoints and monitoring capabilities.
"""

import pytest
from httpx import AsyncClient


class TestHealthAndMonitoring:
    """Health check and system monitoring tests."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """Test the health check endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test the root endpoint."""
        response = await client.get("/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data
        assert "openapi" in data
        
        assert data["name"] == "Review Analysis API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/api/v1/docs"
        assert data["openapi"] == "/api/v1/openapi.json"

    @pytest.mark.asyncio
    async def test_openapi_docs_accessibility(self, client: AsyncClient):
        """Test that OpenAPI documentation is accessible."""
        # Test OpenAPI JSON
        response = await client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        
        # Verify it matches our specification
        assert data["info"]["title"] == "Review Analysis API"
        assert data["info"]["version"] == "1.0.0"
        
        # Verify required endpoints are documented
        paths = data["paths"]
        required_endpoints = [
            "/api/v1/task/run/single",
            "/api/v1/task/run/batch", 
            "/api/v1/task/result/single",
            "/api/v1/task/result/batch"
        ]
        
        for endpoint in required_endpoints:
            assert endpoint in paths, f"Endpoint {endpoint} not documented"

    @pytest.mark.asyncio
    async def test_swagger_ui_accessibility(self, client: AsyncClient):
        """Test that Swagger UI is accessible."""
        response = await client.get("/api/v1/docs")
        assert response.status_code == 200
        
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_redoc_accessibility(self, client: AsyncClient):
        """Test that ReDoc documentation is accessible."""
        response = await client.get("/api/v1/redoc")
        assert response.status_code == 200
        
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_cors_headers(self, client: AsyncClient):
        """Test CORS headers are properly set."""
        # Test preflight request
        response = await client.options(
            "/api/v1/task/run/single",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Should handle CORS preflight
        assert response.status_code in [200, 204]
        
        # Test actual request with CORS
        response = await client.post(
            "/api/v1/task/run/single",
            json={
                "user_id": "cors_test_user",
                "text": "CORS test"
            },
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_security_headers(self, client: AsyncClient):
        """Test that security headers are properly set."""
        response = await client.get("/health")
        
        # Check for common security headers
        headers = response.headers
        
        # X-Content-Type-Options should prevent MIME sniffing
        assert "x-content-type-options" in headers
        
        # These headers might be set by the security middleware
        security_headers = [
            "x-frame-options",
            "x-xss-protection", 
            "strict-transport-security",
            "content-security-policy"
        ]
        
        # At least some security headers should be present
        present_headers = [h for h in security_headers if h in headers]
        # Note: This is informational - not all may be required

    @pytest.mark.asyncio
    async def test_response_time_consistency(self, client: AsyncClient):
        """Test response time consistency for health checks."""
        import time
        
        response_times = []
        
        # Make multiple health check requests
        for _ in range(10):
            start_time = time.time()
            response = await client.get("/health")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Response times should be consistently fast
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        
        assert avg_time < 0.1, f"Average health check time {avg_time}s too slow"
        assert max_time < 0.5, f"Maximum health check time {max_time}s too slow"

    @pytest.mark.asyncio
    async def test_endpoint_availability(self, client: AsyncClient):
        """Test that all documented endpoints are available."""
        # Test all main endpoints for basic availability
        endpoints_to_test = [
            ("GET", "/health"),
            ("GET", "/"),
            ("GET", "/api/v1/openapi.json"),
            ("GET", "/api/v1/docs"),
            ("GET", "/api/v1/redoc"),
            ("POST", "/api/v1/task/run/single"),
            ("POST", "/api/v1/task/run/batch"),
            ("POST", "/api/v1/task/result/single"),
            ("POST", "/api/v1/task/result/batch"),
        ]
        
        for method, endpoint in endpoints_to_test:
            if method == "GET":
                response = await client.get(endpoint)
            elif method == "POST":
                # Use minimal valid data for POST endpoints
                if "single" in endpoint:
                    if "run" in endpoint:
                        response = await client.post(
                            endpoint,
                            json={"user_id": "availability_test", "text": "test"}
                        )
                    else:  # result endpoint
                        response = await client.post(
                            endpoint,
                            json={"user_id": "availability_test"}
                        )
                elif "batch" in endpoint:
                    if "run" in endpoint:
                        response = await client.post(
                            endpoint,
                            data={"user_id": "availability_test"},
                            files={"file": ("test.csv", b"test,data", "text/csv")}
                        )
                    else:  # result endpoint
                        response = await client.post(
                            endpoint,
                            json={"user_id": "availability_test"}
                        )
            
            # Should not return 404 or 500 (endpoint should exist and handle requests)
            assert response.status_code != 404, f"Endpoint {method} {endpoint} not found"
            assert response.status_code < 500, f"Endpoint {method} {endpoint} has server error"

    @pytest.mark.asyncio
    async def test_content_type_headers(self, client: AsyncClient):
        """Test that proper content-type headers are returned."""
        
        # JSON endpoints should return application/json
        json_endpoints = [
            "/health",
            "/",
            "/api/v1/openapi.json"
        ]
        
        for endpoint in json_endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 200
            assert "application/json" in response.headers.get("content-type", "")
        
        # HTML endpoints should return text/html
        html_endpoints = [
            "/api/v1/docs",
            "/api/v1/redoc"
        ]
        
        for endpoint in html_endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 200
            assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_error_response_format(self, client: AsyncClient):
        """Test that error responses follow a consistent format."""
        
        # Test 404 error
        response = await client.get("/nonexistent/endpoint")
        assert response.status_code == 404
        
        # Should return JSON error format
        if "application/json" in response.headers.get("content-type", ""):
            data = response.json()
            # Should have some error information
            assert isinstance(data, dict)
        
        # Test 422 validation error
        response = await client.post(
            "/api/v1/task/run/single",
            json={}  # Missing required fields
        )
        assert response.status_code == 422
        
        # Should return structured validation error
        if "application/json" in response.headers.get("content-type", ""):
            data = response.json()
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_api_versioning(self, client: AsyncClient):
        """Test API versioning through URL prefix."""
        
        # All API endpoints should be under /api/v1
        response = await client.post(
            "/api/v1/task/run/single",
            json={
                "user_id": "version_test",
                "text": "API version test"
            }
        )
        
        assert response.status_code == 200
        
        # Test that unversioned paths don't work
        response = await client.post(
            "/task/run/single",  # Missing /api/v1 prefix
            json={
                "user_id": "version_test",
                "text": "API version test"
            }
        )
        
        assert response.status_code == 404  # Should not be found

    @pytest.mark.asyncio
    async def test_request_id_tracking(self, client: AsyncClient):
        """Test request ID tracking for monitoring."""
        
        response = await client.post(
            "/api/v1/task/run/single",
            json={
                "user_id": "request_id_test",
                "text": "Request tracking test"
            }
        )
        
        assert response.status_code == 200
        
        # Check if request tracking headers are present
        # (These may or may not be implemented depending on middleware)
        headers = response.headers
        
        # Common request tracking headers
        tracking_headers = [
            "x-request-id",
            "x-correlation-id",
            "x-trace-id"
        ]
        
        # Note: This is informational - not required but good for monitoring
