from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password_hash: str
    phone_number: Optional[str] = None
    birthday: Optional[datetime] = None
    time_of_pregnancy: Optional[int] = None 
    blood_type: Optional[str] = None 
    weight: Optional[float] = None
    height: Optional[float] = None

    role: str = Field(default="user")  # pregnant_woman | midwife | admin
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_verified: bool = Field(default=False)  # For midwives, indicates if they are verified by admin
    current_subscription_id: Optional[int] = Field(foreign_key="subscription.id", default=None)

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    message: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
