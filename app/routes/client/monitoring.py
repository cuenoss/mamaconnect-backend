from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.monitoring import MonitoringResponse, LogCreate
from app.dependencies import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.models.monitoring import Logs

router = APIRouter(tags=["Client", "Monitoring"])


@router.get("/belt", response_model=MonitoringResponse)
async def get_belt_monitoring(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    metrics = ["heartbeat", "temperature", "spo2", "movement", "kicks"]
    readings = {}

    for metric in metrics:
        result = await db.execute(
            select(Logs)
            .where(
                Logs.user_id == current_user.id,
                Logs.description == metric
            )
            .order_by(Logs.timestamp.desc())
            .limit(1)
        )

        log = result.scalar_one_or_none()
        readings[metric] = log.value if log else None

    return {
        "device_status": "Connected & Syncing",
        "battery": 87,  # optional if not stored yet
        "heartbeat": {
            "bpm": readings["heartbeat"],
            "status": "Normal",
            "normal_range": "120 – 160 BPM"
        },
        "kicks": {
            "kicks_today": readings["kicks"],
            "status": "Normal",
            "expected": "10+ per day"
        },
        "temperature": {
            "value": readings["temperature"],
            "status": "Normal",
            "normal_range": "36.1 – 37.2 °C"
        },
        "movement": {
            "percent": readings["movement"],
            "status": "Active"
        },
        "oxygen": {
            "spo2": readings["spo2"],
            "status": "Normal",
            "normal_range": "95 – 100%"
        },
        "manual_kick_counter": readings["kicks"],
        "notifications": []
    }



@router.post("/belt/data")
async def receive_belt_data(
    log: LogCreate,
    db: AsyncSession = Depends(get_db)
):
    new_log = Logs(**log.dict())
    db.add(new_log)
    await db.commit()
    return {"message": "Sensor data saved"}