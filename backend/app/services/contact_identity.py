"""
Contact Identity Service.
Handles normalization and canonical resolution of contact identities.
"""

from sqlalchemy.orm import Session
from app.models.contact_identity import ContactIdentity


def get_or_create_contact_identity(contact_type: str, contact_value: str, db: Session) -> ContactIdentity:
    """
    Fetches an existing canonical identity by type and normalized value,
    or creates and returns a new one.
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
        identity = ContactIdentity(
            contact_type=c_type,
            normalized_value=c_val,
        )
        db.add(identity)
        db.flush()

    return identity