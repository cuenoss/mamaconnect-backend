from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime, timedelta
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.database import get_async_session
from app.models.user import User
from app.models.monitoring import Appointment
from app.schemas.midwife import MidwifeDashboardResponse, AppointmentResponse, AssignedClient
from app.dependencies import get_current_user  

router = APIRouter( tags=["Midwife Dashboard"])


@router.get("/dashboard", response_model=MidwifeDashboardResponse)
async def get_midwife_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):

    if current_user.role != "midwife":
        raise HTTPException(status_code=403, detail="Not authorized")

    today = datetime.utcnow()
    week_end = today + timedelta(days=7)

    # Total clients
    stmt = (
        select(Appointment.client_id)
        .where(Appointment.midwife_id == current_user.id)
        .distinct()
    )
    result = await db.execute(stmt)
    total_clients = result.scalars().all()
    total_clients_count = len(total_clients)

    # Upcoming appointments
    stmt = (
        select(Appointment)
        .where(Appointment.midwife_id == current_user.id)
        .where(Appointment.date >= today)
        .where(Appointment.date <= week_end)
        .order_by(Appointment.date)
    )
    result = await db.execute(stmt)
    upcoming_appointments = result.scalars().all()
    upcoming_count = len(upcoming_appointments)

    # Completed appointments this week
    week_start = today - timedelta(days=today.weekday())

    stmt = (
        select(Appointment)
        .where(Appointment.midwife_id == current_user.id)
        .where(Appointment.status == "completed")
        .where(Appointment.date >= week_start)
        .where(Appointment.date <= week_end)
    )
    result = await db.execute(stmt)
    completed_appointments = result.scalars().all()
    completed_count = len(completed_appointments)

    unread_messages = 5

    appointments_list = [
        AppointmentResponse(
            id=appt.id,
            date=appt.date.date(),
            time=appt.date.time(),
            status=appt.status,
            location=appt.location
        )
        for appt in upcoming_appointments
    ]

    return MidwifeDashboardResponse(
        greeting=f"Welcome back, {current_user.name}",
        member_since=current_user.created_at.year,
        today=today.date(),
        total_clients=total_clients_count,
        upcoming_appointments_count=upcoming_count,
        completed_consultations_count=completed_count,
        unread_messages=unread_messages,
        appointments=appointments_list
    )


@router.get("/clients", response_model=list[AssignedClient])
def get_assigned_clients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_async_session),
    risk_filter: str | None = Query(None, description="Optional risk filter: low, medium, high"),
):
    
    if current_user.role != "midwife":
        raise HTTPException(status_code=403, detail="Not authorized")

    stmt = select(User).where(User.id == current_user.id)
    if risk_filter:
        stmt = stmt.where(User.risk_level.ilike(risk_filter)) 

    clients = db.exec(stmt).all()
    today=date.today()

    clients_list = []
    for c in clients:
        clients_list.append({
            "id": c.id,
            "initials": f"{c.name.split()[0]}{c.name.split()[1]}",
            "name": f"{c.name}",
            "age": today.year-c.birthday.year,
            "risk_level": c.risk_level.capitalize(),
            "pregnancy_week": f"{c.time_of_pregnancy}/{40}",
            "due_date": c.due_date,
            "last_checkin": c.last_checkin,
        })

    return clients_list