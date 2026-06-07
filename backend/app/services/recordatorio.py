import logging
from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.database import engine
from app.models.domain import Raffle, RaffleStatus, Reservation, ReservationStatus
from app.services.notifications import send_whatsapp

logger = logging.getLogger(__name__)

_VENTANA_DIAS = 1  # draw_date en [14, 16] días


def send_payment_reminders() -> None:
    """Job diario: envía recordatorio WhatsApp a compradores con reserva pendiente
    cuya rifa sortea en exactamente 15 días (tolerancia ±1 día). Idempotente."""
    try:
        with Session(engine) as session:
            _procesar_recordatorios(session)
    except Exception:
        logger.exception("Error ejecutando job de recordatorios de pago")


def _procesar_recordatorios(session: Session) -> None:
    ahora = datetime.utcnow()
    desde = ahora + timedelta(days=15 - _VENTANA_DIAS)
    hasta = ahora + timedelta(days=15 + _VENTANA_DIAS)

    reservas = session.exec(
        select(Reservation, Raffle)
        .join(Raffle, Raffle.id == Reservation.raffle_id)
        .where(
            Reservation.status == ReservationStatus.pending,
            Reservation.reminder_sent_at.is_(None),
            Raffle.status == RaffleStatus.active,
            Raffle.draw_date >= desde,
            Raffle.draw_date <= hasta,
        )
    ).all()

    for reservation, raffle in reservas:
        _enviar_recordatorio(session, reservation, raffle)


def _enviar_recordatorio(session: Session, reservation: Reservation, raffle: Raffle) -> None:
    settings = get_settings()
    enviado = send_whatsapp(
        reservation.buyer_phone,
        settings.meta_template_payment_reminder,
        {
            "buyer_name": reservation.buyer_name,
            "number": reservation.number,
            "raffle_name": raffle.name,
            "draw_date": raffle.draw_date.strftime("%d/%m/%Y"),
            "expires_at": reservation.expires_at.strftime("%d/%m/%Y"),
        },
    )
    if enviado:
        reservation.reminder_sent_at = datetime.utcnow()
        session.add(reservation)
        session.commit()
    else:
        logger.warning(
            "No se pudo enviar recordatorio a %s para reserva %s",
            reservation.buyer_phone,
            reservation.id,
        )
