import uuid
from datetime import datetime
from pydantic import BaseModel

class HcpBase(BaseModel):
    name: str
    specialty: str
    hospital: str
    city: str
    prescription_preferences: dict | None = None

class HcpCreate(HcpBase):
    pass

class HcpRead(HcpBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
