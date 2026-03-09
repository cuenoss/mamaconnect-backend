from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class License(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    midwife_id: int = Field(foreign_key="user.id")
    status: str = Field(default="pending")  # pending | approved | rejected

    license_number: Optional[str] = None
    certificate_file: Optional[str] = None
    national_id: Optional[str] = None

    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None


class Alergies(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    allergen: str
    reaction: str
    severity: str  # mild | moderate | severe


class Illness(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    illness_name: str
    diagnosis_date: datetime
    treatment: Optional[str] = None


class Medication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    medication_name: str
    dosage: str
    start_date: datetime
    end_date: Optional[datetime] = None


class HospitalVisit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    visit_date: datetime
    reason: str
    doctor_name: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None
