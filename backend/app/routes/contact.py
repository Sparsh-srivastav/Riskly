from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.contact import Contact
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactResponse


router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"],
)


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = Contact(
        owner_id=current_user.id,
        contact_value=data.contact_value,
        contact_type=data.contact_type,
        label=data.label,
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact


@router.get(
    "",
    response_model=list[ContactResponse],
)
def get_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.scalars(
        select(Contact)
        .where(Contact.owner_id == current_user.id)
        .order_by(Contact.created_at.desc())
    ).all()


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = db.scalar(
        select(Contact).where(
            Contact.id == contact_id,
            Contact.owner_id == current_user.id,
        )
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    db.delete(contact)
    db.commit()