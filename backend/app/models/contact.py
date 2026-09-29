from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            "contact_value",
            "contact_type",
            name="uq_contact_owner_value_type",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    contact_value: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    contact_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )