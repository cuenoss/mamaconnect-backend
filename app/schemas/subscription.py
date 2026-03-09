from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PlanFeature(BaseModel):
    feature: str

class PlanResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    currency: str
    billing_period: str
    features: List[str]
    is_most_popular: bool
    is_active: bool
    
    class Config:
        from_attributes = True

class SubscriptionCreate(BaseModel):
    plan_id: int
    payment_method: Optional[str] = None

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    payment_method: Optional[str]
    plan: PlanResponse
    
    class Config:
        from_attributes = True

class UserSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    plan: PlanResponse
    
    class Config:
        from_attributes = True
