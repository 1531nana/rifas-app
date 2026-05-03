from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import get_current_admin
from app.core.database import get_session
from app.models.domain import Admin, Raffle
from app.models.schemas import RaffleCreate, RaffleDetailRead, RaffleRead, ReservationRead
from app.services.raffles import confirm_cash_payment, create_raffle, get_owned_raffle, get_raffle_detail

router = APIRouter(prefix="/raffles", tags=["raffles"])


@router.get("", response_model=list[RaffleRead])
def list_raffles(
    current_admin: Admin = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> list[Raffle]:
    return list(session.exec(select(Raffle).where(Raffle.admin_id == current_admin.id)).all())


@router.post("", response_model=RaffleRead, status_code=201)
def create_raffle_endpoint(
    payload: RaffleCreate,
    current_admin: Admin = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> Raffle:
    return create_raffle(session, current_admin.id or 0, payload)


@router.get("/{raffle_id}", response_model=RaffleDetailRead)
def get_raffle_endpoint(
    raffle_id: int,
    current_admin: Admin = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> RaffleDetailRead:
    raffle = get_owned_raffle(session, current_admin.id or 0, raffle_id)
    return get_raffle_detail(session, raffle)


@router.post("/{raffle_id}/reservations/{reservation_id}/confirm-cash", response_model=ReservationRead)
def confirm_cash_payment_endpoint(
    raffle_id: int,
    reservation_id: int,
    current_admin: Admin = Depends(get_current_admin),
    session: Session = Depends(get_session),
):
    raffle = get_owned_raffle(session, current_admin.id or 0, raffle_id)
    return confirm_cash_payment(session, raffle, reservation_id)
