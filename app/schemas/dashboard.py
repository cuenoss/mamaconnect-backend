from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PregnancyInfo(BaseModel):
    current_week: int
    current_month: int
    days_remaining: int
    estimated_due_date: Optional[datetime]
    trimester: str
    progress: float
    upcoming_appointments: Optional[str] = None
