from datetime import datetime

from sqlmodel import Session, select

from app.models.domain import Reservation, ReservationStatus


def confirmar_pago(session: Session, reservation_id: int) -> None:
    """Marca una reserva como pagada tras aprobacion de Wompi."""
    reservation = session.exec(
        select(Reservation).where(Reservation.id == reservation_id)
    ).first()
    if reservation is None or reservation.status != ReservationStatus.pending:
        return
    reservation.status = ReservationStatus.paid
    reservation.paid_at = datetime.utcnow()
    session.add(reservation)
    session.commit()


def cancelar_pago(session: Session, reservation_id: int) -> None:
    """Libera un numero al rechazarse o anularse el pago en Wompi."""
    reservation = session.exec(
        select(Reservation).where(Reservation.id == reservation_id)
    ).first()
    if reservation is None or reservation.status != ReservationStatus.pending:
        return
    reservation.status = ReservationStatus.expired
    session.add(reservation)
    session.commit()
