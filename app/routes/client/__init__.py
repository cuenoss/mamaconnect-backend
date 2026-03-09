# Client routes module
from .chatbot import router as chatbot_router
from .dashboard import router as dashboard_router  
from .monitoring import router as monitoring_router
from .booking import router as booking_router

__all__ = ["chatbot_router", "dashboard_router", "monitoring_router", "booking_router"]
