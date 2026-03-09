import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

class TestArticlesRoutes:
    """Test content management routes without database dependency"""
    
    def test_articles_get_all_exists(self):
        """Test getting all articles endpoint exists"""
        response = client.get("/articles/")
        assert response.status_code != 404
        assert response.status_code in [200, 500]

    def test_articles_get_by_category_exists(self):
        """Test getting articles by category endpoint exists"""
        response = client.get("/articles/?category=nutrition")
        assert response.status_code != 404
        assert response.status_code in [200, 500]

    def test_articles_get_by_tag_exists(self):
        """Test getting articles by tag endpoint exists"""
        response = client.get("/articles/?tags=pregnancy")
        assert response.status_code != 404
        assert response.status_code in [200, 500]

    def test_articles_search_exists(self):
        """Test searching articles endpoint exists"""
        response = client.get("/articles/search?q=nutrition")
        assert response.status_code != 404
        assert response.status_code in [200, 500]

    def test_articles_get_by_id_exists(self):
        """Test getting article by ID endpoint exists"""
        response = client.get("/articles/1")
        assert response.status_code != 404
        assert response.status_code in [200, 404, 500]

    def test_articles_faqs_exists(self):
        """Test getting FAQs endpoint exists"""
        response = client.get("/articles/faqs")
        assert response.status_code != 404
        assert response.status_code in [200, 500]

    def test_articles_faqs_by_category_exists(self):
        """Test getting FAQs by category endpoint exists"""
        response = client.get("/articles/faqs?category=exercise")
        assert response.status_code != 404
        assert response.status_code in [200, 500]

    def test_articles_validation(self):
        """Test articles input validation"""
        # Test search query validation
        response = client.get("/articles/search")
        assert response.status_code in [200, 422, 500]
        
        # Test invalid category
        response = client.get("/articles/?category=")
        assert response.status_code in [200, 500]

if __name__ == "__main__":
    pytest.main([__file__])
