"""
Reputation Scoring Engine.
Computes multi-signal risk metrics for global contact identities based on community reports.
"""

from uuid import UUID
from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.contact_identity import ContactIdentity

WEIGHTS = {
    "fraud": 30.0,
    "scam": 25.0,
    "phishing": 25.0,
    "spam": 10.0,
    "harassment": 15.0,
    "other": 5.0,
}


def calculate_identity_reputation(identity_id: UUID | str, db: Session) -> dict:
    """
    Calculates the risk score and explainable breakdown for a specific ContactIdentity.
    Score ranges from 0.0 (safe) to 100.0 (high risk).
    """
    if isinstance(identity_id, str):
        identity_id = UUID(identity_id)

    identity = db.query(ContactIdentity).filter(ContactIdentity.id == identity_id).first()
    if not identity:
        return {
            "score": 0.0,
            "risk_level": "UNKNOWN",
            "report_count": 0,
            "breakdown": {},
        }

    reports = db.query(Report).filter(Report.identity_id == identity_id).all()
    if not reports:
        return {
            "score": 0.0,
            "risk_level": "LOW",
            "report_count": 0,
            "breakdown": {},
        }

    raw_score = 0.0
    breakdown: dict[str, int] = {}

    for report in reports:
        rtype = report.report_type.lower().strip()
        breakdown[rtype] = breakdown.get(rtype, 0) + 1
        raw_score += WEIGHTS.get(rtype, 5.0)

    score = min(round(raw_score, 2), 100.0)

    if score >= 60.0:
        risk_level = "HIGH"
    elif score >= 25.0:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "score": score,
        "risk_level": risk_level,
        "report_count": len(reports),
        "breakdown": breakdown,
    }