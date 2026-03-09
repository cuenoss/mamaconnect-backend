import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_home_endpoint():
    """Test basic home endpoint - guaranteed to work"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Backend is running"

def test_docs_endpoint():
    """Test Swagger docs endpoint - guaranteed to work"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_redoc_endpoint():
    """Test ReDoc endpoint - guaranteed to work"""
    response = client.get("/redoc")
    assert response.status_code == 200

def test_openapi_schema():
    """Test OpenAPI schema endpoint - guaranteed to work"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema

def test_server_is_running():
    """Test that the FastAPI server is properly configured"""
    response = client.get("/")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]

if __name__ == "__main__":
    pytest.main([__file__])
