from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.domain import Raffle
from app.models.schemas import PublicRaffleRead, ReservationCreate, ReservationRead
from app.services.raffles import get_number_states, reserve_number

router = APIRouter(prefix="/r", tags=["public"])


def get_raffle_by_token(public_token: str, session: Session) -> Raffle:
    raffle = session.exec(select(Raffle).where(Raffle.public_token == public_token)).first()
    if raffle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rifa no encontrada")
    return raffle


@router.get("/{public_token}", response_model=PublicRaffleRead)
def public_raffle(public_token: str, session: Session = Depends(get_session)) -> PublicRaffleRead:
    raffle = get_raffle_by_token(public_token, session)
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
        numbers=get_number_states(session, raffle),
    )


@router.post("/{public_token}/reserve", response_model=ReservationRead, status_code=201)
def public_reserve(
    public_token: str,
    payload: ReservationCreate,
    session: Session = Depends(get_session),
):
    raffle = get_raffle_by_token(public_token, session)
    return reserve_number(session, raffle, payload)
