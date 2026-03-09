from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BookingCreate(BaseModel):
    midwife_id: int
    session_type: str = Field(..., description="Type of session: Video Call, In-Person, etc.")
    scheduled_time: datetime
    price: float

class BookingUpdate(BaseModel):
    status: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    price: Optional[float] = None

class BookingResponse(BaseModel):
    id: int
    midwife_id: int
    midwife_name: str
    pregnant_woman_id: int
    pregnant_woman_name: Optional[str] = None
    session_type: str
    scheduled_time: datetime
    price: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BookingConfirmation(BaseModel):
    id: int
    midwife_name: str
    session_type: str
    scheduled_time: datetime
    price: float
    status: str
    
    class Config:
        from_attributes = True

class MidwifeInfo(BaseModel):
    id: int
    name: str
    email: str
    is_verified: bool
    
    class Config:
        from_attributes = True

class BookingListResponse(BaseModel):
    bookings: List[BookingResponse]
    total: int
    page: int
    size: int
