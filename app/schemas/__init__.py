# Import all schemas for easy access
from .user import (
    UserCreate, UserProfile, UserProfileUpdate, UserUpdate,
    Token, TokenData, LoginRequest, SignUpRequest
)
from .booking import (
    BookingCreate, BookingUpdate, BookingResponse, 
    BookingConfirmation, MidwifeInfo, BookingListResponse
)
from .dashboard import PregnancyInfo
from .monitoring import LogCreate, MonitoringResponse
from .content import (
    ArticleCreate, ArticleResponse, ArticleCreateRequest,
    FAQCreate, FAQResponse
)
from .chat import (
    ChatRequest, ChatResponse, ChatSessionCreate,
    ChatSessionResponse, ChatMessageResponse
)
from .medical import (
    MidwifeVerificationRequest, MidwifeVerificationResponse,
    MidwifeVerificationReviewRequest, AllergyCreate,
    IllnessCreate, MedicationCreate, HospitalVisitCreate
)
from .midwife import (
    AppointmentResponse, AssignedClient, MidwifeDashboardResponse,
    ClientDetail, ConsultationNote, ConsultationNoteCreate
)
from .monitoring_extended import (
    Heartbeat, Kicks, Temperature, Oxygen, Movement, Notification,
    MonitoringResponseExtended, LogCreateExtended
)
from .admin import (
    UserUpdate, MidWifeUpdate, MidWifeProfileUpdate, ArticleUpdate,
    AdminStats, UserManagementResponse, LicenseVerification, LicenseReview
)

# Export all schemas
__all__ = [
    # User schemas
    "UserCreate", "UserProfile", "UserProfileUpdate", "UserUpdate",
    "Token", "TokenData", "LoginRequest", "SignUpRequest",
    
    # Booking schemas
    "BookingCreate", "BookingUpdate", "BookingResponse", 
    "BookingConfirmation", "MidwifeInfo", "BookingListResponse",
    
    # Dashboard schemas
    "PregnancyInfo",
    
    # Monitoring schemas
    "LogCreate", "MonitoringResponse",
    
    # Content schemas
    "ArticleCreate", "ArticleResponse", "ArticleCreateRequest",
    "FAQCreate", "FAQResponse",
    
    # Chat schemas
    "ChatRequest", "ChatResponse", "ChatSessionCreate",
    "ChatSessionResponse", "ChatMessageResponse",
    
    # Medical schemas
    "MidwifeVerificationRequest", "MidwifeVerificationResponse",
    "MidwifeVerificationReviewRequest", "AllergyCreate",
    "IllnessCreate", "MedicationCreate", "HospitalVisitCreate",
    
    # Midwife schemas
    "AppointmentResponse", "AssignedClient", "MidwifeDashboardResponse",
    "ClientDetail", "ConsultationNote", "ConsultationNoteCreate",
    
    # Extended monitoring schemas
    "Heartbeat", "Kicks", "Temperature", "Oxygen", "Movement", "Notification",
    "MonitoringResponseExtended", "LogCreateExtended",
    
    # Admin schemas
    "UserUpdate", "MidWifeUpdate", "MidWifeProfileUpdate", "ArticleUpdate",
    "AdminStats", "UserManagementResponse", "LicenseVerification", "LicenseReview"
]
