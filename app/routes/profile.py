from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserProfile, UserProfileUpdate
from app.dependencies import get_current_user_with_db

router = APIRouter(tags=["Profile"])

@router.get("/", response_model=UserProfile)
async def get_profile(
    current_user: User = Depends(get_current_user_with_db)
):
    """Get current user profile"""
    return UserProfile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        blood_type=current_user.blood_type,
        height=current_user.height,
        weight=current_user.weight
    )

@router.put("/", response_model=UserProfile)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    
    # Update only provided fields
    update_data = profile_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserProfile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at
    )
