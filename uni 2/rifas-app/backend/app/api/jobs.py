from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_admin
from app.core.database import get_session
from app.models.domain import Admin
from app.services.raffles import expire_all_old_reservations, send_payment_reminders

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/expire-reservations")
def expire_reservations_job(
    _current_admin: Admin = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> dict[str, int]:
    return {"expired": expire_all_old_reservations(session)}


@router.post("/payment-reminders")
def payment_reminders_job(
    _current_admin: Admin = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> dict[str, int]:
    return {"sent": send_payment_reminders(session)}
