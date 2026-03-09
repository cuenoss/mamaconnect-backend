from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Logs(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    log_type: str  # symptom | mood | activity
    description: str #heartneats | blood pressure | weight | temerature |kicks count | contractions 
    value: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    midwife_id: int = Field(foreign_key="user.id")
    appointment_time: datetime
    status: str = Field(default="scheduled")  # scheduled, completed, cancelled
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
