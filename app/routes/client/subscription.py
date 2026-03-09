from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json

from app.database import get_db
from app.models.subscription import Plan, Subscription
from app.models.user import User
from app.schemas.subscription import PlanResponse, SubscriptionCreate, SubscriptionResponse, UserSubscriptionResponse
from app.dependencies import get_current_user ,require_admin
from app.middleware.subscription_security import (
    require_subscription_eligibility,
    rate_limit_subscription,
    validate_payment_method,
    check_subscription_status,
    SubscriptionSecurity
)

router = APIRouter(tags=["Client", "Subscription"])

@router.get("/plans", response_model=List[PlanResponse])
async def get_plans(db: Session = Depends(get_db)):
    """Get all available subscription plans"""
    plans = db.query(Plan).filter(Plan.is_active == True).all()
    
    plan_responses = []
    for plan in plans:
        features = json.loads(plan.features) if plan.features else []
        plan_response = PlanResponse(
            id=plan.id,
            name=plan.name,
            description=plan.description,
            price=plan.price,
            currency=plan.currency,
            billing_period=plan.billing_period,
            features=features,
            is_most_popular=plan.is_most_popular,
            is_active=plan.is_active
        )
        plan_responses.append(plan_response)
    
    return plan_responses

@router.post("/subscribe", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_subscription_eligibility
    ),
    _=Depends(rate_limit_subscription("subscribe", max_attempts=3, window_minutes=30))
):
    """Subscribe to a plan with security validations"""
    # Validate payment method
    if subscription_data.payment_method and not validate_payment_method(subscription_data.payment_method):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment method"
        )
    
    # Check if plan exists
    plan = db.query(Plan).filter(Plan.id == subscription_data.plan_id, Plan.is_active == True).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Check if user already has an active subscription
    existing_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True
    ).first()
    
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active subscription"
        )
    
    # Log subscription attempt
    SubscriptionSecurity.log_subscription_action(
        current_user.id, 
        "subscribe_attempt",
        {
            "plan_id": subscription_data.plan_id,
            "payment_method": subscription_data.payment_method,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        },
        db
    )
    
    # Create new subscription
    subscription = Subscription(
        user_id=current_user.id,
        plan_id=subscription_data.plan_id,
        payment_method=subscription_data.payment_method
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    # Update user's current subscription
    current_user.current_subscription_id = subscription.id
    db.commit()
    
    # Log successful subscription
    SubscriptionSecurity.log_subscription_action(
        current_user.id,
        "subscribe_success",
        {
            "subscription_id": subscription.id,
            "plan_id": subscription_data.plan_id
        },
        db
    )
    
    # Get plan details for response
    features = json.loads(plan.features) if plan.features else []
    plan_response = PlanResponse(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        price=plan.price,
        currency=plan.currency,
        billing_period=plan.billing_period,
        features=features,
        is_most_popular=plan.is_most_popular,
        is_active=plan.is_active
    )
    
    return SubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        plan_id=subscription.plan_id,
        start_date=subscription.start_date,
        end_date=subscription.end_date,
        is_active=subscription.is_active,
        payment_method=subscription.payment_method,
        plan=plan_response
    )

@router.get("/current", response_model=UserSubscriptionResponse)
async def get_current_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription"""
    if not current_user.current_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    subscription = db.query(Subscription).filter(
        Subscription.id == current_user.current_subscription_id,
        Subscription.is_active == True
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated plan not found"
        )
    
    features = json.loads(plan.features) if plan.features else []
    plan_response = PlanResponse(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        price=plan.price,
        currency=plan.currency,
        billing_period=plan.billing_period,
        features=features,
        is_most_popular=plan.is_most_popular,
        is_active=plan.is_active
    )
    
    return UserSubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        plan_id=subscription.plan_id,
        start_date=subscription.start_date,
        end_date=subscription.end_date,
        is_active=subscription.is_active,
        plan=plan_response
    )

@router.post("/cancel")
async def cancel_subscription(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(rate_limit_subscription("cancel", max_attempts=3, window_minutes=60))
):
    """Cancel current subscription with security"""
    if not current_user.current_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    subscription = db.query(Subscription).filter(
        Subscription.id == current_user.current_subscription_id,
        Subscription.is_active == True
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    # Log cancellation attempt
    SubscriptionSecurity.log_subscription_action(
        current_user.id,
        "cancel_attempt",
        {
            "subscription_id": subscription.id,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        },
        db
    )
    
    # Deactivate subscription
    subscription.is_active = False
    subscription.end_date = datetime.utcnow()
    
    # Remove from user
    current_user.current_subscription_id = None
    
    db.commit()
    
    # Log successful cancellation
    SubscriptionSecurity.log_subscription_action(
        current_user.id,
        "cancel_success",
        {
            "subscription_id": subscription.id
        },
        db
    )
    
    return {"message": "Subscription cancelled successfully"}

# Admin-only routes for plan management
@router.post("/plans", response_model=PlanResponse)
async def create_plan(
    plan_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new subscription plan (admin only)"""
    # Validate required fields
    required_fields = ["name", "description", "price", "features"]
    for field in required_fields:
        if field not in plan_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    # Convert features list to JSON string
    if isinstance(plan_data["features"], list):
        plan_data["features"] = json.dumps(plan_data["features"])
    
    plan = Plan(**plan_data)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    
    features = json.loads(plan.features) if plan.features else []
    return PlanResponse(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        price=plan.price,
        currency=plan.currency,
        billing_period=plan.billing_period,
        features=features,
        is_most_popular=plan.is_most_popular,
        is_active=plan.is_active
    )

@router.put("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: int,
    plan_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a subscription plan (admin only)"""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Update fields
    for key, value in plan_data.items():
        if hasattr(plan, key):
            if key == "features" and isinstance(value, list):
                setattr(plan, key, json.dumps(value))
            else:
                setattr(plan, key, value)
    
    db.commit()
    db.refresh(plan)
    
    features = json.loads(plan.features) if plan.features else []
    return PlanResponse(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        price=plan.price,
        currency=plan.currency,
        billing_period=plan.billing_period,
        features=features,
        is_most_popular=plan.is_most_popular,
        is_active=plan.is_active
    )
