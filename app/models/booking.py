from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    midwife_id: int = Field(foreign_key="user.id")
    pregnant_woman_id: int = Field(foreign_key="user.id")
    session_type: str  # "Video Call", "In-Person", etc.
    scheduled_time: datetime
    price: float
    status: str = Field(default="confirmed")  # confirmed, pending, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
