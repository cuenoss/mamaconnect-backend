from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import redis
import json
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.dependencies import get_current_user

# Redis client for rate limiting (you'll need to configure Redis)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
except:
    redis_client = None

class SubscriptionSecurity:
    
    @staticmethod
    def rate_limit(user_id: int, action: str, max_attempts: int = 5, window_minutes: int = 60) -> bool:
        """Rate limit subscription actions per user"""
        if not redis_client:
            return True  # Skip rate limiting if Redis not available
            
        key = f"rate_limit:subscription:{user_id}:{action}"
        current = redis_client.get(key)
        
        if current and int(current) >= max_attempts:
            return False
            
        # Increment counter
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_minutes * 60)
        pipe.execute()
        
        return True
    
    @staticmethod
    def validate_subscription_change(user: User, db: Session) -> bool:
        """Validate if user can change subscription"""
        # Check if user has recent subscription changes
        recent_change = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.start_date > datetime.utcnow() - timedelta(days=7)
        ).first()
        
        if recent_change:
            return False
        return True
    
    @staticmethod
    def log_subscription_action(user_id: int, action: str, details: dict, db: Session):
        """Log subscription actions for audit"""
        # You might want to create an AuditLog model
        log_entry = {
            "user_id": user_id,
            "action": action,
            "details": json.dumps(details),
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": details.get("ip_address"),
            "user_agent": details.get("user_agent")
        }
        
        # For now, print to console - in production, save to database or logging service
        print(f"SUBSCRIPTION_AUDIT: {log_entry}")

def require_subscription_eligibility(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user is eligible for subscription changes"""
    if not SubscriptionSecurity.validate_subscription_change(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too recent subscription changes. Please wait before making changes."
        )
    return current_user

def rate_limit_subscription(
    action: str,
    max_attempts: int = 5,
    window_minutes: int = 60
):
    """Rate limiting decorator for subscription endpoints"""
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not SubscriptionSecurity.rate_limit(current_user.id, action, max_attempts, window_minutes):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many {action} attempts. Please try again later."
            )
        return current_user
    return dependency

def validate_payment_method(payment_method: str) -> bool:
    """Basic payment method validation"""
    valid_methods = ["credit_card", "paypal", "bank_transfer", "crypto"]
    return payment_method in valid_methods if payment_method else False

def check_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check and return user's subscription status"""
    if not current_user.current_subscription_id:
        return None
        
    subscription = db.query(Subscription).filter(
        Subscription.id == current_user.current_subscription_id,
        Subscription.is_active == True
    ).first()
    
    return subscription
