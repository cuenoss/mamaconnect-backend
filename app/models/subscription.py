from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Plan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # Basic, Standard, Premium
    description: str
    price: int  # in DA (Algerian Dinar)
    currency: str = Field(default="DA")
    billing_period: str = Field(default="month")  # month, year
    features: str  # JSON string of features array
    is_most_popular: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    plan_id: int = Field(foreign_key="plan.id")
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    is_active: bool = Field(default=True)
    payment_method: Optional[str] = None
    stripe_subscription_id: Optional[str] = None  # For future payment integration
    created_at: datetime = Field(default_factory=datetime.utcnow)
