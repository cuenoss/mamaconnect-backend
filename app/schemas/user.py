from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: str

class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_verified: bool
    created_at: datetime
    blood_type: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    birthday: Optional[datetime] = None
    time_of_pregnancy: Optional[int] = None
    

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=72)
    is_active: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    user_id: int
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str

class SignUpRequest(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str
    role: str
    
    
