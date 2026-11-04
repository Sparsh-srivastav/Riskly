import os
import sys
import logging
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from ml.classifier import classifier

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.contact_identity import ContactIdentity
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportResponse, IdentityReputationResponse
from app.services.reputation import calculate_identity_reputation
from app.services.kafka_producer import publish_event
from app.services.ws_manager import manager

logger = logging.getLogger("riskly-reports")

router = APIRouter(prefix="/reports", tags=["Reports & Reputation"])


@router.get("/reputation", response_model=IdentityReputationResponse)
def get_reputation(
    contact_type: str,
    contact_value: str,
    db: Session = Depends(get_db),
):
    c_type = contact_type.strip().lower()
    c_val = contact_value.strip()

    identity = db.scalar(
        select(ContactIdentity).where(
            ContactIdentity.contact_type == c_type,
            ContactIdentity.normalized_value == c_val,
        )
    )

    if not identity:
        return IdentityReputationResponse(
            contact_type=c_type,
            normalized_value=c_val,
            score=0,
            risk_level="LOW",
            report_count=0,
            breakdown={},
        )

    return IdentityReputationResponse(contact_type=c_type, normalized_value=c_val, **calculate_identity_reputation(identity.id, db))


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c_type = payload.contact_type.strip().lower()
    c_val = payload.contact_value.strip()

    ml_result = classifier.analyze(payload.description or "")

    identity = db.scalar(
        select(ContactIdentity).where(
            ContactIdentity.contact_type == c_type,
            ContactIdentity.normalized_value == c_val,
        )
    )

    if not identity:
        identity = ContactIdentity(
            contact_type=c_type,
            normalized_value=c_val,
        )
        db.add(identity)
        db.commit()
        db.refresh(identity)

    report_cat = payload.report_type.strip().lower()
    if report_cat in ["spam", "other"] and ml_result["is_high_risk"]:
        report_cat = ml_result["primary_category"]

    report = Report(
        reporter_id=current_user.id,
        identity_id=identity.id,
        report_type=report_cat,
        description=payload.description,
        evidence=payload.evidence,
        status="pending",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    stream_payload = {
        "report_id": str(report.id),
        "reporter_id": str(report.reporter_id),
        "identity_id": str(report.identity_id),
        "contact_type": identity.contact_type,
        "contact_value": identity.normalized_value,
        "report_type": report.report_type,
        "ml_risk_score": ml_result["ml_risk_score"],
        "detected_flags": ml_result["detected_flags"],
        "urgency_level": ml_result["urgency_level"],
        "created_at": report.created_at.isoformat(),
    }

    # Fire-and-forget background Kafka task without blocking response
    try:
        asyncio.create_task(publish_event(topic="contact-reports", payload=stream_payload))
    except Exception as exc:
        logger.warning("Kafka dispatch failed: %s", exc)

    # Broadcast directly to connected frontend clients
    await manager.broadcast({
        "event": "new_report",
        **stream_payload,
        "description": report.description,
    })

    return ReportResponse(
        id=str(report.id),
        reporter_id=str(report.reporter_id),
        status=report.status,
        identity_id=str(report.identity_id),
        contact_type=identity.contact_type,
        contact_value=identity.normalized_value,
        report_type=report.report_type,
        description=report.description,
        ml_risk_score=ml_result["ml_risk_score"],
        created_at=report.created_at.isoformat(),
    )
