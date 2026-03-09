from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.monitoring import Appointment
from app.models.user import User
from app.schemas.dashboard import PregnancyInfo
from app.dependencies import require_pregnant_woman
from datetime import datetime, timedelta

router = APIRouter(tags=["Client", "Dashboard"])


@router.get("/pregnancy-info", response_model=PregnancyInfo)
async def get_pregnancy_info(current_user: User = Depends(require_pregnant_woman),db: AsyncSession = Depends(get_db)):
    if not current_user.birthday or not current_user.time_of_pregnancy:
        raise HTTPException(status_code=400, detail="Pregnancy information is incomplete.")
    today = datetime.utcnow().date()
    conception_date = current_user.birthday + timedelta(weeks=current_user.time_of_pregnancy)
    days_pregnant = (today - conception_date).days
    current_week = days_pregnant // 7
    current_month = current_week // 4
    days_remaining = (current_user.birthday + timedelta(weeks=40)) - today
    estimated_due_date = current_user.birthday + timedelta(weeks=40)
    if current_week < 13:
        trimester = "First Trimester"
    elif current_week < 27:
        trimester = "Second Trimester"
    else:
        trimester = "Third Trimester"
    pregnancy_info = PregnancyInfo(
        current_week=current_week,
        current_month=current_month,
        days_remaining=days_remaining,
        estimated_due_date=estimated_due_date,
        trimester=trimester,
    )

    appointments_query = select(Appointment).where(Appointment.client_id== current_user.id, Appointment.date >= today).order_by(Appointment.date)
    appointments_result = await db.execute(appointments_query)
    upcoming_appointments = appointments_result.scalars().all()
    pregnancy_info.upcoming_appointments = upcoming_appointments

    return pregnancy_info


