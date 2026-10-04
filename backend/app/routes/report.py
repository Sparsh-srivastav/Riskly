from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.report import Report
from app.models.user import User
from app.models.contact import Contact
from app.schemas.report import ReportCreate, ReportResponse


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = db.scalar(
        select(Contact).where(
            Contact.id == report_data.contact_id
        )
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    report = Report(
        reporter_id=current_user.id,
        contact_id=contact.id,
        report_type=report_data.report_type,
        description=report_data.description,
        evidence=report_data.evidence,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


@router.get(
    "",
    response_model=list[ReportResponse],
)
def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = db.scalars(
        select(Report)
        .where(Report.reporter_id == current_user.id)
        .order_by(Report.created_at.desc())
    ).all()

    return reports


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
)
def get_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.scalar(
        select(Report).where(
            Report.id == report_id,
            Report.reporter_id == current_user.id,
        )
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return report