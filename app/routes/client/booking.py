from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.booking import Booking
from app.schemas.booking import (
    BookingCreate, 
    BookingResponse, 
    BookingConfirmation, 
    MidwifeInfo,
    BookingListResponse
)
from app.dependencies import (
    get_current_user_with_db,
    require_pregnant_woman,
    require_midwife
)

router = APIRouter(tags=["Client", "Booking"])

@router.get("/midwives", response_model=List[MidwifeInfo])
async def get_verified_midwives(
    db: AsyncSession = Depends(get_db)
):
    """Get all verified midwives available for booking"""
    result = await db.execute(
        select(User).where(User.role == "midwife", User.is_verified == True)
    )
    midwives = result.scalars().all()
    
    return [
        MidwifeInfo(
            id=m.id,
            name=m.name,
            email=m.email,
            is_verified=m.is_verified
        ) 
        for m in midwives
    ]

@router.post("/create", response_model=BookingConfirmation)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(require_pregnant_woman),
    db: AsyncSession = Depends(get_db)
):
    """Create a new booking (pregnant women only)"""
    
    # Verify midwife exists and is verified
    midwife_result = await db.execute(
        select(User).where(
            User.id == booking_data.midwife_id, 
            User.role == "midwife", 
            User.is_verified == True
        )
    )
    midwife = midwife_result.scalar_one_or_none()
    if not midwife:
        raise HTTPException(
            status_code=404, 
            detail="Midwife not found or not verified"
        )
    
    # Check for conflicting bookings
    conflict_result = await db.execute(
        select(Booking).where(
            Booking.midwife_id == booking_data.midwife_id,
            Booking.scheduled_time == booking_data.scheduled_time,
            Booking.status != "cancelled"
        )
    )
    existing_booking = conflict_result.scalar_one_or_none()
    if existing_booking:
        raise HTTPException(
            status_code=409,
            detail="This time slot is already booked"
        )
    
    # Create booking
    booking = Booking(
        midwife_id=booking_data.midwife_id,
        pregnant_woman_id=current_user.id,
        session_type=booking_data.session_type,
        scheduled_time=booking_data.scheduled_time,
        price=booking_data.price,
        status="confirmed"
    )
    
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    
    return BookingConfirmation(
        id=booking.id,
        midwife_name=midwife.name,
        session_type=booking.session_type,
        scheduled_time=booking.scheduled_time,
        price=booking.price,
        status=booking.status
    )

@router.get("/my-bookings", response_model=List[BookingResponse])
async def get_user_bookings(
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncSession = Depends(get_db)
):
    """Get bookings for current user (pregnant women or midwives)"""
    
    if current_user.role == "pregnant_woman":
        result = await db.execute(
            select(Booking).where(Booking.pregnant_woman_id == current_user.id)
        )
    elif current_user.role == "midwife":
        result = await db.execute(
            select(Booking).where(Booking.midwife_id == current_user.id)
        )
    else:
        raise HTTPException(
            status_code=403,
            detail="Only pregnant women and midwives can view bookings"
        )
    
    bookings = result.scalars().all()
    
    # Get user details for each booking
    booking_responses = []
    for booking in bookings:
        # Get midwife info
        midwife_result = await db.execute(
            select(User).where(User.id == booking.midwife_id)
        )
        midwife = midwife_result.scalar_one_or_none()
        
        # Get pregnant woman info
        patient_result = await db.execute(
            select(User).where(User.id == booking.pregnant_woman_id)
        )
        patient = patient_result.scalar_one_or_none()
        
        booking_responses.append(BookingResponse(
            id=booking.id,
            midwife_id=booking.midwife_id,
            midwife_name=midwife.name if midwife else "Unknown",
            pregnant_woman_id=booking.pregnant_woman_id,
            pregnant_woman_name=patient.name if patient else "Unknown",
            session_type=booking.session_type,
            scheduled_time=booking.scheduled_time,
            price=booking.price,
            status=booking.status,
            created_at=booking.created_at,
            updated_at=booking.updated_at
        ))
    
    return booking_responses

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking_details(
    booking_id: int,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncSession = Depends(get_db)
):
    """Get specific booking details"""
    
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check permissions
    if (current_user.role == "pregnant_woman" and 
        booking.pregnant_woman_id != current_user.id) or \
       (current_user.role == "midwife" and 
        booking.midwife_id != current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You can only view your own bookings"
        )
    
    # Get user details
    midwife_result = await db.execute(
        select(User).where(User.id == booking.midwife_id)
    )
    midwife = midwife_result.scalar_one_or_none()
    
    patient_result = await db.execute(
        select(User).where(User.id == booking.pregnant_woman_id)
    )
    patient = patient_result.scalar_one_or_none()
    
    return BookingResponse(
        id=booking.id,
        midwife_id=booking.midwife_id,
        midwife_name=midwife.name if midwife else "Unknown",
        pregnant_woman_id=booking.pregnant_woman_id,
        pregnant_woman_name=patient.name if patient else "Unknown",
        session_type=booking.session_type,
        scheduled_time=booking.scheduled_time,
        price=booking.price,
        status=booking.status,
        created_at=booking.created_at,
        updated_at=booking.updated_at
    )

@router.put("/{booking_id}/cancel", response_model=dict)
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user_with_db),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a booking"""
    
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check permissions
    if (current_user.role == "pregnant_woman" and 
        booking.pregnant_woman_id != current_user.id) or \
       (current_user.role == "midwife" and 
        booking.midwife_id != current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You can only cancel your own bookings"
        )
    
    if booking.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Booking is already cancelled"
        )
    
    booking.status = "cancelled"
    booking.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Booking cancelled successfully"}

@router.get("/midwife/availability/{midwife_id}")
async def check_midwife_availability(
    midwife_id: int,
    date: str,  # Format: YYYY-MM-DD
    db: AsyncSession = Depends(get_db)
):
    """Check available time slots for a midwife on a specific date"""
    
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Get all bookings for the midwife on that date
    result = await db.execute(
        select(Booking).where(
            Booking.midwife_id == midwife_id,
            Booking.scheduled_time >= datetime.combine(target_date, datetime.min.time()),
            Booking.scheduled_time < datetime.combine(target_date, datetime.max.time()),
            Booking.status != "cancelled"
        )
    )
    bookings = result.scalars().all()
    
    # Generate available time slots (example: 9 AM to 5 PM, hourly slots)
    booked_times = {b.scheduled_time.hour for b in bookings}
    available_slots = []
    
    for hour in range(9, 18):  # 9 AM to 5 PM
        if hour not in booked_times:
            available_slots.append(f"{hour:02d}:00")
    
    return {
        "midwife_id": midwife_id,
        "date": date,
        "available_slots": available_slots,
        "booked_slots": list(booked_times)
    }
