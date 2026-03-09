from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, time

class Heartbeat(BaseModel):
    bpm: int
    status: str
    normal_range: str

class Kicks(BaseModel):
    kicks_today: int
    status: str
    expected: str

class Temperature(BaseModel):
    value: float
    status: str
    normal_range: str

class Oxygen(BaseModel):
    spo2: float
    status: str
    normal_range: str

class Movement(BaseModel):
    percent: int
    status: str

class Notification(BaseModel):
    type: str
    title: str
    message: str
    time: str

class MonitoringResponseExtended(BaseModel):
    device_status: str
    battery: int
    heartbeat: Heartbeat
    kicks: Kicks
    temperature: Temperature
    movement: Movement
    oxygen: Oxygen
    manual_kick_counter: int
    notifications: List[Notification]

class LogCreateExtended(BaseModel):
    user_id: int
    log_type: str        # symptom | mood | activity | device
    description: str     # heartbeat | temperature | kicks | spo2 | movement
    value: float | int
