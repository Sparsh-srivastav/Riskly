import re
from typing import Dict, Any, List

# Core risk intent keywords and heuristic patterns
SUSPICIOUS_PATTERNS = {
    "phishing": [
        r"\b(otp|one[-\s]time[-\s]password|pin|cvv|password)\b",
        r"\b(click\s+here|login\s+link|verify\s+account|update\s+kyc)\b",
        r"\b(bank\s+alert|debit\s+card|credit\s+card|account\s+suspended)\b",
    ],
    "fraud": [
        r"\b(lottery|prize|won\s+\d+|cashback|reward\s+points)\b",
        r"\b(wire\s+transfer|gift\s+card|crypto|bitcoin|investment\s+return)\b",
        r"\b(guaranteed\s+profit|double\s+your\s+money|customs\s+fee)\b",
    ],
    "urgency": [
        r"\b(urgent|immediate|within\s+\d+\s+hours|action\s+required)\b",
        r"\b(police|legal\s+notice|arrest\s+warrant|court\s+order)\b",
        r"\b(account\s+blocked|sim\s+deactivation)\b",
    ],
    "impersonation": [
        r"\b(customs\s+officer|income\s+tax|cbi|rbi|fedex|courier)\b",
        r"\b(manager|bank\s+executive|tech\s+support|microsoft\s+support)\b",
    ],
}


class FraudTextClassifier:
    """
    Lightweight rule-based and heuristic NLP scorer for incident narratives.
    Extracts semantic signals, matches scam patterns, and generates an ML threat profile.
    """

    def __init__(self):
        self.compiled_rules = {
            category: [re.compile(pat, re.IGNORECASE) for pat in patterns]
            for category, patterns in SUSPICIOUS_PATTERNS.items()
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "ml_risk_score": 0.0,
                "detected_flags": [],
                "primary_category": "none",
                "urgency_level": "low",
                "is_high_risk": False,
            }

        cleaned = text.lower().strip()
        matched_flags: List[str] = []
        category_hits: Dict[str, int] = {cat: 0 for cat in SUSPICIOUS_PATTERNS}

        for cat, patterns in self.compiled_rules.items():
            for regex in patterns:
                matches = regex.findall(cleaned)
                if matches:
                    category_hits[cat] += len(matches)
                    for match in set(matches):
                        matched_flags.append(f"{cat}:{match}")

        # Compute heuristic weighted score (0 - 100)
        score = 0.0
        score += min(category_hits["phishing"] * 25.0, 50.0)
        score += min(category_hits["fraud"] * 25.0, 50.0)
        score += min(category_hits["urgency"] * 15.0, 30.0)
        score += min(category_hits["impersonation"] * 20.0, 40.0)

        normalized_score = min(round(score, 2), 100.0)

        # Determine dominant classification category
        primary_category = "spam"
        if category_hits["phishing"] > 0 and category_hits["phishing"] >= category_hits["fraud"]:
            primary_category = "phishing"
        elif category_hits["fraud"] > 0:
            primary_category = "fraud"

        urgency_level = "high" if category_hits["urgency"] > 1 else ("medium" if category_hits["urgency"] == 1 else "low")

        return {
            "ml_risk_score": normalized_score,
            "detected_flags": matched_flags,
            "primary_category": primary_category,
            "urgency_level": urgency_level,
            "is_high_risk": normalized_score >= 60.0,
        }


# Global reusable instance
classifier = FraudTextClassifier()