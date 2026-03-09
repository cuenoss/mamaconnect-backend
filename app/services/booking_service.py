from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from app.models import Booking, User
from app.schemas import BookingCreate, BookingResponse, BookingConfirmation, MidwifeInfo
from typing import List, Optional


async def get_verified_midwives(db: AsyncSession) -> List[MidwifeInfo]:
    """Get all verified midwives"""
    result = await db.execute(
        select(User).where(User.role == "midwife", User.is_verified == True)
    )
    midwives = result.scalars().all()
    return [MidwifeInfo(id=m.id, name=m.name, email=m.email, is_verified=m.is_verified) 
            for m in midwives]


async def create_booking(
    db: AsyncSession, 
    booking_data: BookingCreate, 
    pregnant_woman_id: int
) -> BookingConfirmation:
    """Create a new booking"""
    # Verify midwife exists and is verified
    midwife_result = await db.execute(
        select(User).where(User.id == booking_data.midwife_id, User.role == "midwife", User.is_verified == True)
    )
    midwife = midwife_result.scalar_one_or_none()
    if not midwife:
        raise ValueError("Midwife not found or not verified")
    
    # Create booking
    booking = Booking(
        midwife_id=booking_data.midwife_id,
        pregnant_woman_id=pregnant_woman_id,
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


async def get_user_bookings(
    db: AsyncSession, 
    user_id: int, 
    user_role: str
) -> List[BookingResponse]:
    """Get bookings for a user (either as pregnant woman or midwife)"""
    if user_role == "pregnant_woman":
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.midwife_id))
            .where(Booking.pregnant_woman_id == user_id)
        )
    elif user_role == "midwife":
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.pregnant_woman_id))
            .where(Booking.midwife_id == user_id)
        )
    else:
        raise ValueError("Invalid user role for booking retrieval")
    
    bookings = result.scalars().all()
    
    # Get midwife names for each booking
    booking_responses = []
    for booking in bookings:
        # Get midwife info
        midwife_result = await db.execute(select(User).where(User.id == booking.midwife_id))
        midwife = midwife_result.scalar_one_or_none()
        
        booking_responses.append(BookingResponse(
            id=booking.id,
            midwife_id=booking.midwife_id,
            midwife_name=midwife.name if midwife else "Unknown",
            pregnant_woman_id=booking.pregnant_woman_id,
            session_type=booking.session_type,
            scheduled_time=booking.scheduled_time,
            price=booking.price,
            status=booking.status,
            created_at=booking.created_at
        ))
    
    return booking_responses


async def get_booking_by_id(db: AsyncSession, booking_id: int) -> Optional[BookingResponse]:
    """Get a specific booking by ID"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        return None
    
    # Get midwife info
    midwife_result = await db.execute(select(User).where(User.id == booking.midwife_id))
    midwife = midwife_result.scalar_one_or_none()
    
    return BookingResponse(
        id=booking.id,
        midwife_id=booking.midwife_id,
        midwife_name=midwife.name if midwife else "Unknown",
        pregnant_woman_id=booking.pregnant_woman_id,
        session_type=booking.session_type,
        scheduled_time=booking.scheduled_time,
        price=booking.price,
        status=booking.status,
        created_at=booking.created_at
    )


async def cancel_booking(db: AsyncSession, booking_id: int, user_id: int, user_role: str) -> bool:
    """Cancel a booking"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise ValueError("Booking not found")
    
    # Check if user has permission to cancel this booking
    if user_role == "pregnant_woman" and booking.pregnant_woman_id != user_id:
        raise ValueError("You can only cancel your own bookings")
    elif user_role == "midwife" and booking.midwife_id != user_id:
        raise ValueError("You can only cancel your own bookings")
    
    booking.status = "cancelled"
    booking.updated_at = datetime.utcnow()
    
    await db.commit()
    return True
