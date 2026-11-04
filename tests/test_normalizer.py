import os
import sys
import pytest

# Ensure backend directory is in the Python module path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.normalizer import (
    normalize_identifier,
    normalize_phone_number,
    normalize_email,
    NormalizationError,
)


def test_normalize_email():
    raw_email = "  TEST.User+tag@Example.COM  "
    normalized_type, normalized_val = normalize_identifier("email", raw_email)

    assert normalized_type == "email"
    assert normalized_val == "test.user+tag@example.com"


def test_normalize_phone():
    raw_phone = "+91 98765-43210"
    normalized_type, normalized_val = normalize_identifier("phone", raw_phone)

    assert normalized_type == "phone"
    assert normalized_val == "+919876543210"


def test_invalid_email_format():
    with pytest.raises(NormalizationError):
        normalize_email("not-an-email")


def test_invalid_phone_empty():
    with pytest.raises(NormalizationError):
        normalize_phone_number("   ")