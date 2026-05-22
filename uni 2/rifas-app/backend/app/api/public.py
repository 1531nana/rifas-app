from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.domain import Raffle
from app.models.schemas import CheckoutResponse, PublicRaffleRead, ReservationCreate, ReservationRead
from app.services.raffles import create_wompi_checkout, get_number_states, reserve_number

router = APIRouter(prefix="/r", tags=["public"])


def get_raffle_by_token(public_token: str, session: Session) -> Raffle:
    raffle = session.exec(select(Raffle).where(Raffle.public_token == public_token)).first()
    if raffle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rifa no encontrada")
    return raffle


def build_public_raffle_response(session: Session, raffle: Raffle) -> PublicRaffleRead:
    return PublicRaffleRead(
        id=raffle.id or 0,
        name=raffle.name,
        lottery_type=raffle.lottery_type,
        total_numbers=raffle.total_numbers,
        ticket_price=raffle.ticket_price,
        prize_description=raffle.prize_description,
        draw_date=raffle.draw_date,
        prize_image_url=raffle.prize_image_url,
        public_token=raffle.public_token,
        status=raffle.status,
        winner_number=raffle.winner_number,
        numbers=get_number_states(session, raffle),
    )


@router.get("/{public_token}", response_model=PublicRaffleRead)
def public_raffle(public_token: str, session: Session = Depends(get_session)) -> PublicRaffleRead:
    raffle = get_raffle_by_token(public_token, session)
    return build_public_raffle_response(session, raffle)


@router.get("/{public_token}/numbers")
def public_numbers(public_token: str, session: Session = Depends(get_session)):
    raffle = get_raffle_by_token(public_token, session)
    return get_number_states(session, raffle)


@router.post("/{public_token}/reserve", response_model=ReservationRead, status_code=201)
def public_reserve(
    public_token: str,
    payload: ReservationCreate,
    session: Session = Depends(get_session),
):
    raffle = get_raffle_by_token(public_token, session)
    return reserve_number(session, raffle, payload)


@router.post("/{public_token}/reservations/{reservation_id}/checkout", response_model=CheckoutResponse)
def public_checkout(
    public_token: str,
    reservation_id: int,
    session: Session = Depends(get_session),
) -> CheckoutResponse:
    raffle = get_raffle_by_token(public_token, session)
    return create_wompi_checkout(session, reservation_id, raffle)


compat_router = APIRouter(prefix="/public", tags=["public"])


@compat_router.get("/raffles/{public_token}", response_model=PublicRaffleRead)
def public_raffle_compat(public_token: str, session: Session = Depends(get_session)) -> PublicRaffleRead:
    raffle = get_raffle_by_token(public_token, session)
    return build_public_raffle_response(session, raffle)


@compat_router.get("/raffles/{public_token}/numbers")
def public_numbers_compat(public_token: str, session: Session = Depends(get_session)):
    raffle = get_raffle_by_token(public_token, session)
    return get_number_states(session, raffle)


@compat_router.post("/raffles/{public_token}/reservations", response_model=ReservationRead, status_code=201)
def public_reserve_compat(
    public_token: str,
    payload: ReservationCreate,
    session: Session = Depends(get_session),
):
    raffle = get_raffle_by_token(public_token, session)
    return reserve_number(session, raffle, payload)


@compat_router.post("/reservations/{reservation_id}/checkout", response_model=CheckoutResponse)
def public_checkout_compat(
    reservation_id: int,
    session: Session = Depends(get_session),
) -> CheckoutResponse:
    return create_wompi_checkout(session, reservation_id)
