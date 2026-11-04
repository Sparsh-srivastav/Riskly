"""
Contact normalization utility.
Ensures phone numbers, emails, and identifiers adhere to standard canonical formats
for cross-user fraud aggregation and identity resolution.
"""

import re
from typing import Literal

SupportedIdentityType = Literal["phone", "email"]


class NormalizationError(ValueError):
    """Raised when an identifier cannot be parsed into a standard representation."""
    pass


def normalize_phone_number(raw_phone: str) -> str:
    """
    Normalizes a phone number into an international E.164-like representation.
    Strips whitespace, hyphens, brackets, and periods.
    Ensures valid digit count and standardizes prefix.
    """
    cleaned = re.sub(r"[\s\-\(\)\.]+", "", raw_phone.strip())
    
    if not cleaned:
        raise NormalizationError("Phone number cannot be empty.")

    # Retain '+' if present, ensure remaining characters are purely digits
    if cleaned.startswith("+"):
        digits = cleaned[1:]
        if not digits.isdigit() or len(digits) < 7 or len(digits) > 15:
            raise NormalizationError(f"Invalid international phone number format: '{raw_phone}'.")
        return f"+{digits}"
    
    if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 15:
        raise NormalizationError(f"Invalid phone number digits: '{raw_phone}'.")

    # If no country code is present, default to national/raw cleaned digits
    return cleaned


def normalize_email(raw_email: str) -> str:
    """
    Standardizes email addresses to lowercase and strips extraneous spaces.
    Validates general structure.
    """
    cleaned = raw_email.strip().lower()
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, cleaned):
        raise NormalizationError(f"Invalid email address format: '{raw_email}'.")
    return cleaned


def normalize_identifier(identity_type: str, raw_value: str) -> tuple[str, str]:
    """
    Canonical entry point for identifier normalization.
    Returns a tuple of (normalized_type, normalized_value).
    """
    normalized_type = identity_type.strip().lower()

    if normalized_type == "phone":
        return normalized_type, normalize_phone_number(raw_value)
    elif normalized_type == "email":
        return normalized_type, normalize_email(raw_value)
    else:
        # Default fallback for custom channels (e.g. 'handle', 'upi_id')
        cleaned_value = raw_value.strip().lower()
        if not cleaned_value:
            raise NormalizationError("Identifier value cannot be empty.")
        return normalized_type, cleaned_value