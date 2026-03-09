from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MidwifeVerificationRequest(BaseModel):
    license_number: str
    certificate_file: str
    national_id: str

class MidwifeVerificationResponse(BaseModel):
    id: int
    midwife_id: int
    status: str
    license_number: Optional[str] = None
    certificate_file: Optional[str] = None
    national_id: Optional[str] = None
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MidwifeVerificationReviewRequest(BaseModel):
    status: str  # approved | rejected

class AllergyCreate(BaseModel):
    allergen: str
    reaction: str
    severity: str  # mild | moderate | severe

class IllnessCreate(BaseModel):
    illness_name: str
    diagnosis_date: datetime
    treatment: Optional[str] = None

class MedicationCreate(BaseModel):
    medication_name: str
    dosage: str
    start_date: datetime
    end_date: Optional[datetime] = None

class HospitalVisitCreate(BaseModel):
    visit_date: datetime
    reason: str
    doctor_name: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None
