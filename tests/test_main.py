"""
Tests for main application endpoints
"""
import pytest
from fastapi import status


class TestMainEndpoints:
    """Test class for main application endpoints"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_follow(self, client):
        """Test following the root redirect"""
        response = client.get("/")
        
        # Should eventually reach the static HTML file
        # Note: This might return 404 if static files aren't mounted in test,
        # but the redirect should work
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_api_documentation_available(self, client):
        """Test that FastAPI automatic documentation is available"""
        # Test OpenAPI JSON schema
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        
        openapi_data = response.json()
        assert "openapi" in openapi_data
        assert "info" in openapi_data
        assert "paths" in openapi_data
        
        # Check that our endpoints are documented
        paths = openapi_data["paths"]
        assert "/activities" in paths
        assert "/activities/{activity_name}/signup" in paths
        assert "/activities/{activity_name}/participants/{email}" in paths

    def test_docs_endpoint(self, client):
        """Test that Swagger UI docs are available"""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "").lower()

    def test_redoc_endpoint(self, client):
        """Test that ReDoc documentation is available"""
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "").lower()


class TestApplicationInfo:
    """Test application configuration and info"""

    def test_app_title_and_description(self, client):
        """Test that the app has correct title and description"""
        response = client.get("/openapi.json")
        openapi_data = response.json()
        
        info = openapi_data["info"]
        assert info["title"] == "Mergington High School API"
        assert "API for viewing and signing up for extracurricular activities" in info["description"]

    def test_endpoints_exist_in_openapi(self, client):
        """Test that all expected endpoints are documented in OpenAPI"""
        response = client.get("/openapi.json")
        openapi_data = response.json()
        
        paths = openapi_data["paths"]
        
        # Check GET /activities
        assert "/activities" in paths
        assert "get" in paths["/activities"]
        
        # Check POST /activities/{activity_name}/signup
        signup_path = "/activities/{activity_name}/signup"
        assert signup_path in paths
        assert "post" in paths[signup_path]
        
        # Check DELETE /activities/{activity_name}/participants/{email}
        delete_path = "/activities/{activity_name}/participants/{email}"
        assert delete_path in paths
        assert "delete" in paths[delete_path]

    def test_response_headers(self, client):
        """Test that responses have appropriate headers"""
        response = client.get("/activities")
        
        assert response.status_code == status.HTTP_200_OK
        assert "application/json" in response.headers.get("content-type", "").lower()


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_endpoints(self, client):
        """Test requests to non-existent endpoints"""
        response = client.get("/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_methods(self, client):
        """Test invalid HTTP methods on valid endpoints"""
        # Try to POST to /activities (should be GET only)
        response = client.post("/activities")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # Try to GET signup endpoint (should be POST only)
        response = client.get("/activities/Chess%20Club/signup")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED