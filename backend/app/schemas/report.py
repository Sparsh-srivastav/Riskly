from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReportCreate(BaseModel):
    contact_id: UUID
    report_type: str = Field(min_length=1, max_length=30)
    description: str | None = None
    evidence: str | None = None


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reporter_id: UUID
    contact_id: UUID
    report_type: str
    description: str | None
    evidence: str | None
    status: str
    created_at: datetime