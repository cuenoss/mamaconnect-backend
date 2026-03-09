from pydantic import BaseModel
from typing import List, Optional

class LogCreate(BaseModel):
    user_id: int
    log_type: str
    description: str
    value: Optional[str] = None

class MonitoringResponse(BaseModel):
    device_status: str
    battery: Optional[int] = None
    heartbeat: dict
    kicks: dict
    temperature: dict
    movement: dict
    oxygen: dict
    manual_kick_counter: Optional[int] = None
    notifications: List[str] = []
