import uuid
from datetime import date, datetime
from pydantic import BaseModel

class InteractionProductSchema(BaseModel):
    product_id: uuid.UUID
    name: str

class InteractionBase(BaseModel):
    hcp_id: uuid.UUID
    visit_date: date
    raw_notes: str
    summary: str | None = None
    extracted_entities: dict | None = None
    samples_given: list[dict] | None = None
    action_items: list[dict] | None = None
    follow_up_date: date | None = None
    source: str

class InteractionCreate(InteractionBase):
    products_discussed: list[uuid.UUID] = []  # list of product IDs

class InteractionRead(BaseModel):
    id: uuid.UUID
    hcp_id: uuid.UUID
    hcp_name: str | None = None
    hcp_specialty: str | None = None
    hcp_hospital: str | None = None
    representative_id: uuid.UUID
    visit_date: date
    summary: str | None = None
    raw_notes: str
    extracted_entities: dict | None = None
    samples_given: list[dict] | None = None
    action_items: list[dict] | None = None
    follow_up_date: date | None = None
    source: str
    products_discussed: list[str] = []  # list of product names
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
