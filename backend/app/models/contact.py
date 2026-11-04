import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.contact_identity import ContactIdentity


class Contact(Base):
    """
    User-specific address book entry.
    """
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    identity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("contact_identities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    contact_value: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_type: Mapped[str] = mapped_column(String(20), nullable=False)
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    identity: Mapped["ContactIdentity"] = relationship(
        "ContactIdentity", back_populates="contacts"
    )

    __table_args__ = (
        Index(
            "uq_owner_contact_type_value",
            "owner_id",
            "contact_type",
            "contact_value",
            unique=True,
        ),
    )