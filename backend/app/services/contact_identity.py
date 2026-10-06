from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contact_identity import ContactIdentity


def normalize_contact_value(contact_type: str, contact_value: str) -> str:
    value = contact_value.strip()

    if contact_type.lower() == "email":
        return value.lower()

    if contact_type.lower() == "phone":
        return "".join(
            character
            for character in value
            if character.isdigit() or character == "+"
        )

    return value


def get_or_create_contact_identity(
    db: Session,
    contact_type: str,
    contact_value: str,
) -> ContactIdentity:
    normalized_value = normalize_contact_value(
        contact_type,
        contact_value,
    )

    identity = db.scalar(
        select(ContactIdentity).where(
            ContactIdentity.contact_type == contact_type,
            ContactIdentity.normalized_value == normalized_value,
        )
    )

    if identity:
        return identity

    identity = ContactIdentity(
        contact_type=contact_type,
        normalized_value=normalized_value,
    )

    db.add(identity)
    db.flush()

    return identity