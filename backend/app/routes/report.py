from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.report import Report
from app.models.contact_identity import ContactIdentity
from app.models.user import User
from app.schemas.report import ReportCreate
from app.services.ws_manager import manager

router = APIRouter(prefix="/reports", tags=["Reports"])

class TriageUpdate(BaseModel):
    urgency_level: Optional[str] = None
    ml_risk_score: Optional[int] = None
    status: Optional[str] = None

def get_or_create_system_user(db: Session) -> uuid.UUID:
    user = db.query(User).filter(User.email == "analyst@riskly.dev").first()
    if not user:
        user = db.query(User).first()
    if not user:
        user = User(
            email="analyst@riskly.dev",
            hashed_password="mock_password_hash",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user.id

@router.get("/analytics/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    total_reports = db.query(Report).count()
    total_identities = db.query(ContactIdentity).count()
    
    escalated_count = db.query(Report).filter(Report.status.in_(["critical", "flagged", "escalated"])).count()

    category_counts = db.query(Report.report_type, func.count(Report.id)).group_by(Report.report_type).all()
    categories = {cat.lower(): count for cat, count in category_counts if cat}
    for k in ["fraud", "phishing", "impersonation", "harassment", "spam"]:
        categories.setdefault(k, 0)

    return {
        "total_reports": total_reports,
        "total_identities": total_identities,
        "high_risk_identities": escalated_count,
        "reports_per_min": 24.0 if total_reports > 0 else 0,
        "active_subscribers": len(manager.active_connections),
        "categories": categories
    }

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db)
):
    c_type = payload.contact_type.lower()
    c_val = payload.contact_value.strip()

    identity = db.query(ContactIdentity).filter(
        ContactIdentity.contact_type == c_type,
        ContactIdentity.normalized_value == c_val
    ).first()

    if not identity:
        identity = ContactIdentity(
            contact_type=c_type,
            normalized_value=c_val
        )
        db.add(identity)
        db.commit()
        db.refresh(identity)

    reporter_id = get_or_create_system_user(db)

    initial_status = "critical" if payload.report_type in ["fraud", "phishing"] else "pending"
    report = Report(
        reporter_id=reporter_id,
        identity_id=identity.id,
        report_type=payload.report_type.lower(),
        description=payload.description,
        evidence=payload.evidence,
        status=initial_status
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    ml_conf = 85 if payload.report_type in ["fraud", "impersonation"] else 45
    urgency = "critical" if report.status == "critical" else "low"

    await manager.broadcast({
        "id": str(report.id),
        "contact_type": identity.contact_type,
        "contact_value": identity.normalized_value,
        "report_type": report.report_type,
        "description": report.description,
        "status": report.status,
        "ml_risk_score": ml_conf,
        "urgency_level": urgency,
        "created_at": str(report.created_at)
    })

    return {
        "id": str(report.id),
        "contact_type": identity.contact_type,
        "contact_value": identity.normalized_value,
        "report_type": report.report_type,
        "description": report.description,
        "status": report.status,
        "ml_risk_score": ml_conf,
        "urgency_level": urgency
    }

@router.patch("/{report_id}/triage")
async def update_report_triage(
    report_id: str,
    payload: TriageUpdate,
    db: Session = Depends(get_db)
):
    try:
        parsed_uuid = uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Report UUID format")

    report = db.query(Report).filter(Report.id == parsed_uuid).first()
    if not report:
        raise HTTPException(status_code=404, detail="Incident report not found")

    new_status = payload.status or payload.urgency_level or "escalated"
    report.status = new_status.lower()
    db.commit()
    db.refresh(report)

    identity = db.query(ContactIdentity).filter(ContactIdentity.id == report.identity_id).first()

    event_payload = {
        "event_type": "triage_mutation",
        "id": str(report.id),
        "contact_value": identity.normalized_value if identity else "",
        "urgency_level": "critical" if report.status in ["critical", "escalated"] else "low",
        "ml_risk_score": payload.ml_risk_score if payload.ml_risk_score is not None else 85
    }
    await manager.broadcast(event_payload)

    return {"status": "success", "report": event_payload}
