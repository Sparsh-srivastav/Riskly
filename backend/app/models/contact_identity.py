import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from sqlalchemy import DateTime, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.contact import Contact
    from app.models.report import Report


class ContactIdentity(Base):
    """
    Canonical global identifier for an entity (phone, email, etc.).
    Preserves historical community risk scores even if individual users delete contacts.
    """
    __tablename__ = "contact_identities"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Map Python attributes to existing Postgres column names (identity_type, identity_value)
    contact_type: Mapped[str] = mapped_column(
        "identity_type", String(20), nullable=False
    )
    normalized_value: Mapped[str] = mapped_column(
        "identity_value", String(255), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relational mappings
    contacts: Mapped[List["Contact"]] = relationship(
        "Contact", back_populates="identity"
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report", back_populates="identity"
    )

    __table_args__ = (
        Index("uq_contact_type_normalized_value", "identity_type", "identity_value", unique=True),
    )