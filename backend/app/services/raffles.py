from datetime import datetime, timedelta
from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.domain import PaymentMethod, Raffle, RaffleStatus, Reservation, ReservationStatus
from app.models.schemas import NumberState, RaffleCreate, RaffleDetailRead, ReservationCreate


def create_public_token(session: Session) -> str:
    while True:
        token = token_urlsafe(8)
        exists = session.exec(select(Raffle).where(Raffle.public_token == token)).first()
        if not exists:
            return token


def create_raffle(session: Session, admin_id: int, payload: RaffleCreate) -> Raffle:
    raffle = Raffle(
        admin_id=admin_id,
        name=payload.name,
        lottery_type=payload.lottery_type,
        total_numbers=payload.total_numbers,
        ticket_price=payload.ticket_price,
        prize_description=payload.prize_description,
        draw_date=payload.draw_date,
        prize_image_url=payload.prize_image_url,
        public_token=create_public_token(session),
    )
    session.add(raffle)
    session.commit()
    session.refresh(raffle)
    return raffle


def get_owned_raffle(session: Session, admin_id: int, raffle_id: int) -> Raffle:
    raffle = session.exec(
        select(Raffle).where(
            Raffle.id == raffle_id,
            Raffle.admin_id == admin_id,
        )
    ).first()
    if raffle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rifa no encontrada")
    return raffle


def expire_old_reservations(session: Session, raffle_id: int) -> None:
    now = datetime.utcnow()
    expired = session.exec(
        select(Reservation).where(
            Reservation.raffle_id == raffle_id,
            Reservation.status == ReservationStatus.pending,
            Reservation.expires_at <= now,
        )
    ).all()
    for reservation in expired:
        reservation.status = ReservationStatus.expired
        session.add(reservation)
    if expired:
        session.commit()


def get_number_states(session: Session, raffle: Raffle) -> list[NumberState]:
    expire_old_reservations(session, raffle.id or 0)
    active_reservations = session.exec(
        select(Reservation).where(
            Reservation.raffle_id == raffle.id,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.paid]),
        )
    ).all()
    reserved_by_number = {reservation.number: reservation.status for reservation in active_reservations}

    states: list[NumberState] = []
    for number in range(raffle.total_numbers):
        reservation_status = reserved_by_number.get(number)
        if reservation_status == ReservationStatus.paid:
            status_value = "sold"
        elif reservation_status == ReservationStatus.pending:
            status_value = "reserved"
        else:
            status_value = "available"
        states.append(NumberState(number=number, status=status_value))
    return states


def get_raffle_detail(session: Session, raffle: Raffle) -> RaffleDetailRead:
    expire_old_reservations(session, raffle.id or 0)
    reservations = list(
        session.exec(
            select(Reservation)
            .where(Reservation.raffle_id == raffle.id)
            .order_by(Reservation.created_at.desc())
        ).all()
    )
    active = [
        reservation
        for reservation in reservations
        if reservation.status in [ReservationStatus.pending, ReservationStatus.paid]
    ]
    sold_count = sum(1 for reservation in active if reservation.status == ReservationStatus.paid)
    reserved_count = sum(1 for reservation in active if reservation.status == ReservationStatus.pending)

    return RaffleDetailRead(
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
        sold_count=sold_count,
        reserved_count=reserved_count,
        available_count=raffle.total_numbers - sold_count - reserved_count,
        paid_total=sold_count * raffle.ticket_price,
        reservations=reservations,
    )


def reserve_number(session: Session, raffle: Raffle, payload: ReservationCreate) -> Reservation:
    if raffle.status != RaffleStatus.active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La rifa no esta activa")
    if payload.number >= raffle.total_numbers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Numero fuera del rango de la rifa")

    expire_old_reservations(session, raffle.id or 0)
    existing = session.exec(
        select(Reservation).where(
            Reservation.raffle_id == raffle.id,
            Reservation.number == payload.number,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.paid]),
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El numero ya no esta disponible")

    timeout = timedelta(days=5) if payload.payment_method == PaymentMethod.cash else timedelta(hours=48)
    reservation = Reservation(
        raffle_id=raffle.id or 0,
        number=payload.number,
        buyer_name=payload.buyer_name,
        buyer_phone=payload.buyer_phone,
        buyer_email=payload.buyer_email,
        payment_method=payload.payment_method,
        expires_at=datetime.utcnow() + timeout,
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


def confirm_cash_payment(session: Session, raffle: Raffle, reservation_id: int) -> Reservation:
    reservation = session.exec(
        select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.raffle_id == raffle.id,
        )
    ).first()
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    if reservation.payment_method != PaymentMethod.cash:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solo se confirma efectivo manualmente")
    if reservation.status != ReservationStatus.pending:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La reserva no esta pendiente")

    reservation.status = ReservationStatus.paid
    reservation.paid_at = datetime.utcnow()
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation
