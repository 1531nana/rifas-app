from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.config import get_settings
from app.models.domain import Raffle, RaffleStatus, Reservation, ReservationStatus
from app.models.schemas import RegisterWinnerRequest
from app.services.notifications import send_whatsapp


def register_winner(session: Session, raffle: Raffle, payload: RegisterWinnerRequest) -> Raffle:
    if raffle.status != RaffleStatus.active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La rifa ya esta cerrada")

    winning_reservation = session.exec(
        select(Reservation).where(
            Reservation.raffle_id == raffle.id,
            Reservation.number == payload.number,
            Reservation.status == ReservationStatus.paid,
        )
    ).first()
    if winning_reservation is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El numero ganador no tiene una boleta pagada",
        )

    raffle.winner_number = payload.number
    raffle.status = RaffleStatus.closed
    session.add(raffle)
    session.commit()
    session.refresh(raffle)

    _notificar_ganador(winning_reservation, raffle)
    return raffle


def _notificar_ganador(reservation: Reservation, raffle: Raffle) -> None:
    settings = get_settings()
    send_whatsapp(
        reservation.buyer_phone,
        settings.meta_template_winner_notification,
        {
            "buyer_name": reservation.buyer_name,
            "number": reservation.number,
            "prize_description": raffle.prize_description,
            "raffle_name": raffle.name,
        },
    )
