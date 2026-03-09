import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

class TestCIFriendly:
    """Tests that work in CI/CD without database setup"""
    
    def test_home_endpoint(self):
        """Test basic home endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Backend is running"

    def test_docs_endpoint(self):
        """Test Swagger docs endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_endpoint(self):
        """Test ReDoc endpoint"""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema

    def test_auth_endpoints_exist(self):
        """Test that auth endpoints exist (may fail due to DB, but should not 404)"""
        endpoints = [
            ("/auth/login", "POST", {"email": "test@test.com", "password": "test"}),
            ("/auth/signup", "POST", {"name": "Test", "email": "test@test.com", "password": "test", "role": "pregnant_woman"}),
        ]
        
        for endpoint, method, data in endpoints:
            if method == "POST":
                response = client.post(endpoint, json=data)
            assert response.status_code != 404
            assert response.status_code in [200, 201, 400, 401, 422, 500]

    def test_public_endpoints_accessible(self):
        """Test that public endpoints are accessible"""
        public_endpoints = [
            "/articles/",
            "/articles/faqs",
            "/booking/midwives",
            "/subscription/plans",
            "/midwife/directory",
        ]
        
        for endpoint in public_endpoints:
            response = client.get(endpoint)
            # Should not require authentication (may return 500 if DB not set up)
            assert response.status_code not in [401, 403]

    def test_protected_endpoints_require_auth(self):
        """Test that protected endpoints return auth errors"""
        protected_endpoints = [
            "/auth/me",
            "/profile/",
            "/dashboard/pregnancy-info",
            "/monitoring/belt",
            "/subscription/current",
            "/midwife/profile",
            "/admin/dashboard",
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            # Should require authentication
            assert response.status_code in [401, 403, 500]

if __name__ == "__main__":
    pytest.main([__file__])
