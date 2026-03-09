from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class MidWifeUpdate(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=8, max_length=72)
    role: str = "midwife"
    is_active: bool = True
    is_verified: bool = False

class MidWifeProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None

class AdminStats(BaseModel):
    total_users: int
    total_midwives: int
    total_pregnant_women: int
    total_bookings: int
    pending_verifications: int
    active_sessions: int

class UserManagementResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LicenseVerification(BaseModel):
    id: int
    midwife_id: int
    midwife_name: str
    license_number: Optional[str] = None
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LicenseReview(BaseModel):
    status: str  # approved | rejected
    review_notes: Optional[str] = None
