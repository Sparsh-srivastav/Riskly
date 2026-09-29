from datetime import datetime

from pydantic import BaseModel, Field


class ContactCreate(BaseModel):
    contact_value: str = Field(min_length=1, max_length=255)
    contact_type: str = Field(min_length=1, max_length=20)
    label: str | None = Field(default=None, max_length=100)


class ContactResponse(BaseModel):
    id: str
    contact_value: str
    contact_type: str
    label: str | None
    created_at: datetime