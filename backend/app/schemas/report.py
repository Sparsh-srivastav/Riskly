from datetime import datetime
from uuid import UUID
from typing import Literal, Optional, Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.normalizer import normalize_identifier, NormalizationError

ContactTypeEnum = Literal["phone", "email", "upi", "bank_account", "url"]
ReportTypeEnum = Literal["fraud", "phishing", "spam", "impersonation", "harassment", "other"]

class ReportCreate(BaseModel):
    contact_type: ContactTypeEnum
    contact_value: str = Field(..., min_length=3, max_length=255)
    report_type: ReportTypeEnum = "fraud"
    description: Optional[str] = Field(None, max_length=2000)
    evidence: Optional[str] = Field(None, max_length=1000)

    @field_validator("contact_value", mode="before")
    @classmethod
    def clean_and_normalize(cls, v: str, info) -> str:
        if not isinstance(v, str):
            raise ValueError("Contact value must be a string")
        v = v.strip()
        if not v:
            raise ValueError("Contact value cannot be empty")
        
        c_type = info.data.get("contact_type") if info.data else None
        if c_type:
            try:
                _, normalized = normalize_identifier(c_type, v)
                return normalized
            except NormalizationError as e:
                raise ValueError(str(e))
        return v

    @field_validator("contact_type", mode="before")
    @classmethod
    def canonicalize_type(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("report_type", mode="before")
    @classmethod
    def canonicalize_report_type(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reporter_id: UUID
    identity_id: UUID
    report_type: str
    description: Optional[str] = None
    evidence: Optional[str] = None
    status: str
    created_at: datetime


class IdentityReputationResponse(BaseModel):
    identity_id: Optional[UUID] = None
    contact_type: str
    normalized_value: str
    score: int
    risk_level: str
    report_count: int
    breakdown: Dict[str, int]
