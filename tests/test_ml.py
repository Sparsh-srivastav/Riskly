import os
import sys

# Ensure root workspace is available in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.classifier import classifier


def test_clean_text_no_flags():
    result = classifier.analyze("Hello, this was a legitimate call from my aunt.")
    assert result["ml_risk_score"] == 0.0
    assert result["is_high_risk"] is False
    assert len(result["detected_flags"]) == 0


def test_otp_phishing_detection():
    text = "Caller claimed to be bank executive asking for my urgent OTP and card CVV to unblock account."
    result = classifier.analyze(text)
    assert result["ml_risk_score"] >= 60.0
    assert result["primary_category"] == "phishing"
    assert result["is_high_risk"] is True
    assert any("phishing:otp" in flag or "phishing" in flag for flag in result["detected_flags"])


def test_lottery_fraud_detection():
    text = "Won 50000 lottery cash prize! Demanding advance customs fee via wire transfer."
    result = classifier.analyze(text)
    assert result["ml_risk_score"] >= 50.0
    assert result["primary_category"] == "fraud"


def test_empty_description_handling():
    result = classifier.analyze("")
    assert result["ml_risk_score"] == 0.0
    assert result["detected_flags"] == []