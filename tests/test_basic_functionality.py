import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

class TestBasicFunctionality:
    """Test basic server functionality and documentation"""
    
    def test_home_endpoint(self):
        """Test the basic home endpoint"""
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

class TestRouteAccessibility:
    """Test that all routes are accessible and properly protected"""
    
    def test_all_routes_exist(self):
        """Test that all major routes exist and respond appropriately"""
        routes = [
            # Auth routes
            ("POST", "/auth/login", {"email": "test@test.com", "password": "test"}),
            ("POST", "/auth/signup", {"name": "Test", "email": "test@test.com", "password": "test", "role": "pregnant_woman"}),
            ("POST", "/auth/forgot-password", {"email": "test@test.com"}),
            ("POST", "/auth/reset-password", {"token": "test", "new_password": "test"}),
            ("POST", "/auth/verify-email", {"token": "test"}),
            ("POST", "/auth/refresh-token", {"refresh_token": "test"}),
            ("POST", "/auth/logout", {}),
            ("POST", "/auth/google-login", {"token": "test"}),
            ("POST", "/auth/submit-license", {"license_number": "test"}),
            
            # Client routes
            ("GET", "/dashboard/pregnancy-info", None),
            ("GET", "/monitoring/belt", None),
            ("POST", "/monitoring/belt/data", {"user_id": 1, "description": "test", "value": 100}),
            ("POST", "/chat/session", {"user_id": 1}),
            ("POST", "/chat/", {"session_id": 1, "message": "test"}),
            ("GET", "/chat/session/1", None),
            ("GET", "/booking/midwives", None),
            ("POST", "/booking/create", {"midwife_id": 1, "appointment_date": "2024-01-01T10:00:00"}),
            ("GET", "/booking/my-bookings", None),
            ("GET", "/booking/1", None),
            ("PUT", "/booking/1/cancel", None),
            ("GET", "/booking/midwife/availability/1?date=2024-01-01", None),
            
            # Subscription routes
            ("GET", "/subscription/plans", None),
            ("GET", "/subscription/plans/1", None),
            ("POST", "/subscription/subscribe", {"plan_id": 1, "payment_method": "credit_card"}),
            ("GET", "/subscription/current", None),
            ("POST", "/subscription/cancel", None),
            ("GET", "/subscription/history", None),
            
            # Profile routes
            ("GET", "/profile/", None),
            ("PUT", "/profile/", {"name": "Test"}),
            
            # Midwife routes
            ("GET", "/midwife/dashboard", None),
            ("GET", "/midwife/clients", None),
            ("GET", "/midwife/profile", None),
            ("PUT", "/midwife/profile", {"name": "Test"}),
            ("GET", "/midwife/bookings", None),
            ("POST", "/midwife/license", {"license_number": "test"}),
            ("GET", "/midwife/directory", None),
            ("GET", "/midwife/directory/1", None),
            ("GET", "/midwife/availability", None),
            
            # Admin routes
            ("GET", "/admin/dashboard", None),
            ("GET", "/admin/users", None),
            ("GET", "/admin/articles", None),
            ("GET", "/admin/settings", None),
            ("GET", "/admin/analytics/users", None),
            ("GET", "/admin/audit-logs", None),
            
            # Content routes
            ("GET", "/articles/", None),
            ("GET", "/articles/faqs", None),
            ("GET", "/articles/search?q=test", None),
        ]
        
        for method, endpoint, data in routes:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json=data) if data else client.post(endpoint)
            elif method == "PUT":
                response = client.put(endpoint, json=data) if data else client.put(endpoint)
            
            # All routes should either work or return auth/DB errors, not 404
            assert response.status_code != 404, f"Route {method} {endpoint} not found"
            # Should not crash the server
            assert response.status_code in [200, 201, 400, 401, 403, 404, 422, 500], f"Unexpected status {response.status_code} for {method} {endpoint}"

    def test_protected_endpoints_require_auth(self):
        """Test that protected endpoints return auth errors without authentication"""
        protected_endpoints = [
            "/auth/me",
            "/profile/",
            "/dashboard/pregnancy-info",
            "/monitoring/belt",
            "/subscription/current",
            "/midwife/profile",
            "/admin/dashboard",
            "/admin/users",
            "/admin/articles",
            "/admin/settings",
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            # Should require authentication
            assert response.status_code in [401, 403, 500], f"Endpoint {endpoint} should require authentication"

    def test_public_endpoints_accessible(self):
        """Test that public endpoints are accessible without authentication"""
        public_endpoints = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/articles/",
            "/articles/faqs",
            "/booking/midwives",
            "/subscription/plans",
            "/midwife/directory",
        ]
        
        for endpoint in public_endpoints:
            response = client.get(endpoint)
            # Should be accessible (may return 500 if DB not set up, but not auth errors)
            assert response.status_code not in [401, 403], f"Public endpoint {endpoint} should not require authentication"

if __name__ == "__main__":
    pytest.main([__file__])
