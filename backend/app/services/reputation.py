import math
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.report import Report

CATEGORY_WEIGHTS: Dict[str, float] = {
    "impersonation": 35.0,
    "fraud": 30.0,
    "phishing": 25.0,
    "harassment": 20.0,
    "spam": 10.0,
}
DEFAULT_WEIGHT: float = 15.0
HALF_LIFE_DAYS: float = 30.0


def calculate_identity_reputation(identity_id: Any, db: Session) -> Dict[str, Any]:
    """
    Computes real-time threat reputation score using exponential half-life decay
    and a recidivism escalation curve.
    """
    reports: List[Report] = db.scalars(
        select(Report).where(Report.identity_id == identity_id)
    ).all()

    report_count = len(reports)
    if report_count == 0:
        return {
            "score": 0,
            "risk_level": "LOW",
            "report_count": 0,
            "breakdown": {},
            "decayed_weight_sum": 0.0,
            "recidivism_multiplier": 1.0,
        }

    now_utc = datetime.now(timezone.utc)
    decay_constant = math.log(2) / HALF_LIFE_DAYS

    breakdown: Dict[str, int] = {}
    weighted_score = 0.0

    for rep in reports:
        cat = (rep.report_type or "spam").lower()
        breakdown[cat] = breakdown.get(cat, 0) + 1
        base_weight = CATEGORY_WEIGHTS.get(cat, DEFAULT_WEIGHT)

        # Ensure created_at is timezone-aware
        created_at = rep.created_at
        if created_at is not None:
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            delta_days = max(0.0, (now_utc - created_at).total_seconds() / 86400.0)
        else:
            delta_days = 0.0

        decay_factor = math.exp(-decay_constant * delta_days)
        weighted_score += base_weight * decay_factor

    # Recidivism multiplier: +25% per additional report past the first
    recidivism_multiplier = 1.0 + (0.25 * max(0, report_count - 1))
    escalated_score = weighted_score * recidivism_multiplier

    # Cap at 100
    final_score = int(min(100, round(escalated_score)))

    # Threat tier
    if final_score >= 85:
        risk_level = "CRITICAL"
    elif final_score >= 60:
        risk_level = "HIGH"
    elif final_score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "score": final_score,
        "risk_level": risk_level,
        "report_count": report_count,
        "breakdown": breakdown,
        "decayed_weight_sum": round(weighted_score, 2),
        "recidivism_multiplier": round(recidivism_multiplier, 2),
    }
