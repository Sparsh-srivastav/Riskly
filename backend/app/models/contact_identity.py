from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ContactIdentity(Base):
    __tablename__ = "contact_identities"

    __table_args__ = (
        UniqueConstraint(
            "contact_type",
            "normalized_value",
            name="uq_contact_identity_type_value",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    contact_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    normalized_value: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )