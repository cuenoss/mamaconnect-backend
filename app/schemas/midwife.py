from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, time, datetime

class AppointmentResponse(BaseModel):
    id: int
    patient_initials: str
    patient_name: str
    pregnancy_week: int
    date: date
    time: time
    status: str  # upcoming | completed | cancelled
    type: str    # Clinic Visit, Video Call, Home Visit, etc.
    location: Optional[str] = None
    
    class Config:
        from_attributes = True

class AssignedClient(BaseModel):
    id: int
    initials: str
    name: str
    age: int
    risk_level: str
    pregnancy_week: str
    due_date: date
    last_checkin: date
    
    class Config:
        from_attributes = True

class MidwifeDashboardResponse(BaseModel):
    greeting: str
    risk_status: str
    member_since: int
    today: date
    total_clients: int
    upcoming_appointments_count: int
    completed_consultations_count: int
    unread_messages: int
    appointments: List[AppointmentResponse]
    
    class Config:
        from_attributes = True

class ClientDetail(BaseModel):
    id: int
    name: str
    email: str
    phone_number: Optional[str] = None
    pregnancy_week: int
    due_date: date
    risk_level: str
    last_checkin: datetime
    medical_history: Optional[str] = None
    
    class Config:
        from_attributes = True

class ConsultationNote(BaseModel):
    appointment_id: int
    client_id: int
    notes: str
    recommendations: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[date] = None

class ConsultationNoteCreate(BaseModel):
    appointment_id: int
    client_id: int
    notes: str
    recommendations: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[date] = None
