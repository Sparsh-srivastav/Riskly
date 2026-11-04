from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.contact_identity import ContactIdentity
from app.models.report import Report
from app.services.reputation import calculate_identity_reputation

router = APIRouter(prefix="/contacts", tags=["Contacts & Threat Dossier"])


@router.get("/export-dossier")
def export_threat_dossier(
    contact_type: str,
    contact_value: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates a structured forensic audit report for an entity,
    detailing aggregated threat metrics, incident logs, and analyst timestamps.
    """
    c_type = contact_type.strip().lower()
    c_val = contact_value.strip()

    identity = (
        db.query(ContactIdentity)
        .filter(
            ContactIdentity.contact_type == c_type,
            ContactIdentity.normalized_value == c_val,
        )
        .first()
    )

    if not identity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No forensic records found for {c_val}",
        )

    metrics = calculate_identity_reputation(identity.id, db)
    reports = (
        db.query(Report)
        .filter(Report.identity_id == identity.id)
        .order_by(Report.created_at.desc())
        .all()
    )

    incident_log = [
        {
            "report_id": str(r.id),
            "report_type": r.report_type,
            "description": r.description,
            "evidence": r.evidence,
            "status": r.status,
            "reported_at": r.created_at.isoformat() if hasattr(r, "created_at") and r.created_at else None,
        }
        for r in reports
    ]

    first_seen = reports[-1].created_at.isoformat() if reports and hasattr(reports[-1], "created_at") and reports[-1].created_at else None

    return {
        "dossier_meta": {
            "platform": "Riskly Fraud Intelligence Engine",
            "version": "v0.1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "auditor_email": current_user.email,
        },
        "target_entity": {
            "identity_id": str(identity.id),
            "contact_type": identity.contact_type,
            "normalized_value": identity.normalized_value,
            "first_seen": first_seen,
        },
        "threat_assessment": {
            "risk_score": metrics["score"],
            "risk_level": metrics["risk_level"],
            "total_incidents": metrics["report_count"],
            "signal_breakdown": metrics["breakdown"],
        },
        "incident_history": incident_log,
    }