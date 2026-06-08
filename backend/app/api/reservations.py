from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_admin
from app.core.database import get_session
from app.models.domain import Admin, Reservation
from app.models.schemas import ReservationRead
from app.services.raffles import confirm_cash_payment, get_owned_raffle

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.patch("/{reservation_id}/confirm-cash", response_model=ReservationRead)
def confirm_cash_payment_by_reservation_endpoint(
    reservation_id: int,
    current_admin: Admin = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> Reservation:
    reservation = session.get(Reservation, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    raffle = get_owned_raffle(session, current_admin.id or 0, reservation.raffle_id)
    return confirm_cash_payment(session, raffle, reservation_id)
