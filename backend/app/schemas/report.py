from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ReportCreate(BaseModel):
    contact_type: str
    contact_value: str
    report_type: str
    description: str | None = None
    evidence: str | None = None


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reporter_id: UUID
    identity_id: UUID
    report_type: str
    description: str | None = None
    evidence: str | None = None
    status: str
    created_at: datetime


class IdentityReputationResponse(BaseModel):
    identity_id: UUID | None = None
    contact_type: str
    normalized_value: str
    score: int
    risk_level: str
    report_count: int
    breakdown: dict[str, int]