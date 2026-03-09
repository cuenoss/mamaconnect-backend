import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

class TestClientRoutes:
    """Test all client-facing routes without database dependency"""
    
    def test_dashboard_pregnancy_info_exists(self):
        """Test pregnancy dashboard endpoint exists"""
        response = client.get("/dashboard/pregnancy-info")
        assert response.status_code != 404
        assert response.status_code in [401, 403, 400, 500]

    def test_monitoring_belt_exists(self):
        """Test health monitoring endpoint exists"""
        response = client.get("/monitoring/belt")
        assert response.status_code != 404
        assert response.status_code in [401, 403, 500]

    def test_monitoring_belt_data_exists(self):
        """Test sensor data submission endpoint exists"""
        response = client.post("/monitoring/belt/data", json={
            "user_id": 1,
            "description": "heartbeat",
            "value": 120,
            "timestamp": "2024-01-01T12:00:00"
        })
        assert response.status_code != 404
        assert response.status_code in [200, 401, 422, 500]

    def test_monitoring_belt_data_validation(self):
        """Test monitoring data validation"""
        # Test missing required fields
        response = client.post("/monitoring/belt/data", json={})
        assert response.status_code in [400, 422]
        
        # Test invalid data types
        response = client.post("/monitoring/belt/data", json={
            "user_id": "not_a_number",
            "description": "test",
            "value": "not_a_number"
        })
        assert response.status_code in [400, 422]

    def test_chatbot_create_session_exists(self):
        """Test chatbot session creation endpoint exists"""
        response = client.post("/chat/session", params={"user_id": 1})
        assert response.status_code != 404
        assert response.status_code in [200, 500]

    def test_chatbot_chat_exists(self):
        """Test chatbot interaction endpoint exists"""
        response = client.post("/chat/", json={
            "session_id": 1,
            "message": "Hello"
        })
        assert response.status_code != 404
        assert response.status_code in [404, 422, 500]

    def test_chatbot_get_session_exists(self):
        """Test getting chat session messages endpoint exists"""
        response = client.get("/chat/session/1")
        assert response.status_code != 404
        assert response.status_code in [200, 404, 500]

    def test_chatbot_validation(self):
        """Test chatbot input validation"""
        # Test missing session_id
        response = client.post("/chat/", json={"message": "Hello"})
        assert response.status_code in [400, 422]
        
        # Test missing message
        response = client.post("/chat/", json={"session_id": 1})
        assert response.status_code in [400, 422]

    def test_booking_get_midwives_exists(self):
        """Test getting available midwives endpoint exists"""
        response = client.get("/booking/midwives")
        assert response.status_code != 404
        assert response.status_code in [200, 500]

    def test_booking_create_exists(self):
        """Test creating a booking endpoint exists"""
        response = client.post("/booking/create", json={
            "midwife_id": 1,
            "appointment_date": "2024-06-15T10:00:00",
            "notes": "Regular checkup"
        })
        assert response.status_code != 404
        assert response.status_code in [401, 403, 422, 500]

    def test_booking_my_bookings_exists(self):
        """Test getting user's bookings endpoint exists"""
        response = client.get("/booking/my-bookings")
        assert response.status_code != 404
        assert response.status_code in [401, 403, 500]

    def test_booking_get_details_exists(self):
        """Test getting booking details endpoint exists"""
        response = client.get("/booking/1")
        assert response.status_code != 404
        assert response.status_code in [401, 403, 404, 500]

    def test_booking_cancel_exists(self):
        """Test cancelling a booking endpoint exists"""
        response = client.put("/booking/1/cancel")
        assert response.status_code != 404
        assert response.status_code in [401, 403, 404, 500]

    def test_booking_midwife_availability_exists(self):
        """Test checking midwife availability endpoint exists"""
        response = client.get("/booking/midwife/availability/1?date=2024-06-15")
        assert response.status_code != 404
        assert response.status_code in [200, 404, 500]

    def test_booking_validation(self):
        """Test booking input validation"""
        # Test missing required fields
        response = client.post("/booking/create", json={})
        assert response.status_code in [400, 422]
        
        # Test invalid date format
        response = client.post("/booking/create", json={
            "midwife_id": 1,
            "appointment_date": "invalid-date",
            "notes": "test"
        })
        assert response.status_code in [400, 422]

    def test_subscription_plans_exists(self):
        """Test getting subscription plans endpoint exists"""
        response = client.get("/subscription/plans")
        assert response.status_code != 404
        assert response.status_code in [200, 500]

    def test_subscription_plan_details_exists(self):
        """Test getting specific plan details endpoint exists"""
        response = client.get("/subscription/plans/1")
        assert response.status_code != 404
        assert response.status_code in [200, 404, 500]

    def test_subscription_subscribe_exists(self):
        """Test subscribing to a plan endpoint exists"""
        response = client.post("/subscription/subscribe", json={
            "plan_id": 1,
            "payment_method": "credit_card"
        })
        assert response.status_code != 404
        assert response.status_code in [401, 403, 404, 422, 500]

    def test_subscription_current_exists(self):
        """Test getting current subscription endpoint exists"""
        response = client.get("/subscription/current")
        assert response.status_code != 404
        assert response.status_code in [401, 403, 404, 500]

    def test_subscription_cancel_exists(self):
        """Test cancelling subscription endpoint exists"""
        response = client.post("/subscription/cancel")
        assert response.status_code != 404
        assert response.status_code in [401, 403, 404, 500]

    def test_subscription_history_exists(self):
        """Test subscription history endpoint exists"""
        response = client.get("/subscription/history")
        assert response.status_code != 404
        assert response.status_code in [401, 403, 500]

    def test_subscription_validation(self):
        """Test subscription input validation"""
        # Test missing plan_id
        response = client.post("/subscription/subscribe", json={
            "payment_method": "credit_card"
        })
        assert response.status_code in [400, 422]
        
        # Test invalid payment method
        response = client.post("/subscription/subscribe", json={
            "plan_id": 1,
            "payment_method": "invalid_method"
        })
        assert response.status_code in [400, 422]

if __name__ == "__main__":
    pytest.main([__file__])
