from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.config import Settings, get_settings
from app.core.database import get_session
from app.models.domain import PaymentMethod, Raffle, Reservation, ReservationStatus
from app.models.schemas import NumberState, PublicRaffleRead, ReservationCreate, ReservationRead
from app.models.schemas_pagos import CheckoutResponse
from app.services.raffles import get_number_states, reserve_number
from app.services.wompi import generar_url_checkout, referencia_reserva

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


@router.get("/{public_token}/numbers", response_model=list[NumberState])
def public_raffle_numbers(public_token: str, session: Session = Depends(get_session)) -> list[NumberState]:
    raffle = get_raffle_by_token(public_token, session)
    return get_number_states(session, raffle)


@router.post("/{public_token}/reservations/{reservation_id}/checkout", response_model=CheckoutResponse)
def checkout_wompi(
    public_token: str,
    reservation_id: int,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CheckoutResponse:
    raffle = get_raffle_by_token(public_token, session)
    reservation = session.exec(
        select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.raffle_id == raffle.id,
            Reservation.status == ReservationStatus.pending,
        )
    ).first()
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    if reservation.payment_method == PaymentMethod.cash:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El pago en efectivo no usa checkout digital")

    redirect_url = f"{settings.allowed_origins[0]}/pago/resultado"
    checkout_url = generar_url_checkout(
        reservation=reservation,
        ticket_price=raffle.ticket_price,
        public_key=settings.wompi_public_key,
        integrity_key=settings.wompi_integrity_key,
        redirect_url=redirect_url,
    )
    print(checkout_url)
    return CheckoutResponse(checkout_url=checkout_url, referencia=referencia_reserva(reservation.id or 0))


@router.post("/{public_token}/reserve", response_model=ReservationRead, status_code=201)
def public_reserve(
    public_token: str,
    payload: ReservationCreate,
    session: Session = Depends(get_session),
):
    raffle = get_raffle_by_token(public_token, session)
    return reserve_number(session, raffle, payload)
