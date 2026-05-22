from datetime import datetime, timedelta
from hashlib import sha256
import logging
from pathlib import Path
from secrets import token_urlsafe

from fastapi import HTTPException, UploadFile, status
import httpx
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.config import get_settings
from app.models.domain import PaymentMethod, Raffle, RaffleStatus, Reservation, ReservationStatus
from app.models.schemas import (
    BuyerRead,
    CheckoutResponse,
    NumberState,
    RaffleCreate,
    RaffleDetailRead,
    RaffleStatsRead,
    RaffleUpdate,
    ReservationCreate,
    WebhookResult,
)

IMAGE_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_IMAGE_BYTES = 5 * 1024 * 1024
logger = logging.getLogger(__name__)


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


def update_raffle(session: Session, raffle: Raffle, payload: RaffleUpdate) -> Raffle:
    data = payload.model_dump(exclude_unset=True)
    active_reservations = session.exec(
        select(Reservation).where(
            Reservation.raffle_id == raffle.id,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.paid]),
        )
    ).first()

    locked_fields = {"ticket_price", "total_numbers"}
    if active_reservations and locked_fields.intersection(data):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede cambiar precio o cantidad de numeros con reservas activas",
        )

    for field, value in data.items():
        setattr(raffle, field, value)

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
        winner_number=raffle.winner_number,
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
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El numero ya no esta disponible") from exc
    session.refresh(reservation)
    return reservation


def get_reservation_for_raffle(session: Session, raffle: Raffle, reservation_id: int) -> Reservation:
    reservation = session.exec(
        select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.raffle_id == raffle.id,
        )
    ).first()
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    return reservation


def confirm_cash_payment(session: Session, raffle: Raffle, reservation_id: int) -> Reservation:
    reservation = get_reservation_for_raffle(session, raffle, reservation_id)
    if reservation.payment_method != PaymentMethod.cash:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solo se confirma efectivo manualmente")
    if reservation.status != ReservationStatus.pending:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La reserva no esta pendiente")
    if raffle.status != RaffleStatus.active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La rifa esta cerrada")

    reservation.status = ReservationStatus.paid
    reservation.paid_at = datetime.utcnow()
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    send_payment_confirmation(reservation, raffle)
    return reservation


def create_wompi_checkout(session: Session, reservation_id: int, raffle: Raffle | None = None) -> CheckoutResponse:
    reservation = session.get(Reservation, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    if raffle is None:
        raffle = session.get(Raffle, reservation.raffle_id)
    if raffle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rifa no encontrada")
    if reservation.raffle_id != raffle.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    if raffle.status != RaffleStatus.active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La rifa esta cerrada")
    if reservation.payment_method not in [PaymentMethod.card, PaymentMethod.pse]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La reserva no usa pago digital")
    if reservation.status != ReservationStatus.pending:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La reserva no esta pendiente")

    settings = get_settings()
    reference = str(reservation.id)
    checkout_url = (
        "https://checkout.wompi.co/p/?"
        f"public-key={settings.wompi_public_key}"
        f"&currency=COP&amount-in-cents={raffle.ticket_price * 100}"
        f"&reference={reference}"
        f"&redirect-url={settings.frontend_origin}/payment-result?reference={reference}"
    )
    return CheckoutResponse(checkout_url=checkout_url, reference=reference, sandbox=settings.wompi_public_key.startswith("pub_test"))


def process_wompi_webhook(session: Session, webhook_data: dict) -> WebhookResult:
    if not validate_wompi_signature(webhook_data):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Firma Wompi invalida")

    transaction = webhook_data.get("data", {}).get("transaction") or webhook_data.get("data", {})
    transaction_id = transaction.get("id")
    payment_status = transaction.get("status")
    reference = transaction.get("reference")

    if reference is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Webhook sin referencia")
    try:
        reservation_id = int(reference)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Referencia invalida") from exc

    reservation = session.get(Reservation, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    raffle = session.get(Raffle, reservation.raffle_id)
    if raffle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rifa no encontrada")

    if reservation.wompi_transaction_id and transaction_id and reservation.wompi_transaction_id == transaction_id:
        return WebhookResult(processed=True, status=reservation.status.value, reservation_id=reservation.id)

    if payment_status == "APPROVED":
        reservation.status = ReservationStatus.paid
        reservation.paid_at = datetime.utcnow()
        reservation.wompi_transaction_id = transaction_id
        session.add(reservation)
        session.commit()
        session.refresh(reservation)
        send_payment_confirmation(reservation, raffle)
        return WebhookResult(processed=True, status=reservation.status.value, reservation_id=reservation.id)

    if payment_status in {"DECLINED", "VOIDED", "ERROR"}:
        reservation.status = ReservationStatus.cancelled
        reservation.wompi_transaction_id = transaction_id
        session.add(reservation)
        session.commit()
        return WebhookResult(processed=True, status=reservation.status.value, reservation_id=reservation.id)

    return WebhookResult(processed=False, status=str(payment_status), reservation_id=reservation.id)


def validate_wompi_signature(webhook_data: dict) -> bool:
    settings = get_settings()
    if not settings.wompi_events_secret:
        return True

    signature = webhook_data.get("signature") or {}
    checksum = signature.get("checksum")
    transaction = webhook_data.get("data", {}).get("transaction") or webhook_data.get("data", {})
    raw = f"{transaction.get('id', '')}{transaction.get('status', '')}{transaction.get('reference', '')}{settings.wompi_events_secret}"
    expected = sha256(raw.encode("utf-8")).hexdigest()
    return checksum == expected


def upload_prize_image(session: Session, raffle: Raffle, file: UploadFile) -> Raffle:
    extension = IMAGE_CONTENT_TYPES.get(file.content_type or "")
    if extension is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se aceptan imagenes JPG, PNG o WebP")

    settings = get_settings()
    filename = f"raffle-{raffle.id}-{token_urlsafe(8)}{extension}"
    content = file.file.read(MAX_IMAGE_BYTES + 1)
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="La imagen supera 5MB")

    if settings.cloudinary_cloud_name and settings.cloudinary_upload_preset:
        response = httpx.post(
            f"https://api.cloudinary.com/v1_1/{settings.cloudinary_cloud_name}/image/upload",
            data={"upload_preset": settings.cloudinary_upload_preset, "public_id": filename[: -len(extension)]},
            files={"file": (filename, content, file.content_type)},
            timeout=20,
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Cloudinary rechazo la imagen")
        raffle.prize_image_url = response.json()["secure_url"]
    else:
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        target = upload_dir / filename
        target.write_bytes(content)
        raffle.prize_image_url = f"{settings.app_base_url.rstrip('/')}/uploads/{filename}"

    session.add(raffle)
    session.commit()
    session.refresh(raffle)
    return raffle


def send_payment_confirmation(reservation: Reservation, raffle: Raffle) -> bool:
    return NotificationService().send_whatsapp(
        reservation.buyer_phone,
        "payment_confirmation",
        {
            "buyer_name": reservation.buyer_name,
            "number": reservation.number,
            "raffle_name": raffle.name,
            "draw_date": raffle.draw_date.isoformat(),
        },
    )


class NotificationService:
    def __init__(self, meta_api_token: str | None = None):
        settings = get_settings()
        self.settings = settings
        self.meta_token = meta_api_token or settings.meta_api_token
        self.sandbox_mode = not self.meta_token or not settings.meta_phone_number_id

    def send_whatsapp(self, phone: str, template: str, params: dict | None = None) -> bool:
        if self.sandbox_mode:
            logger.info("[SANDBOX] WhatsApp to %s: %s %s", phone, template, params)
            return True
        try:
            components = []
            if params:
                components.append(
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": str(value)} for value in params.values()],
                    }
                )
            response = httpx.post(
                f"https://graph.facebook.com/v20.0/{self.settings.meta_phone_number_id}/messages",
                headers={"Authorization": f"Bearer {self.meta_token}"},
                json={
                    "messaging_product": "whatsapp",
                    "to": phone,
                    "type": "template",
                    "template": {
                        "name": template,
                        "language": {"code": "es_CO"},
                        "components": components,
                    },
                },
                timeout=10,
            )
            response.raise_for_status()
            return True
        except Exception as exc:
            logger.exception("WhatsApp send error (continuing): %s", exc)
            return False


def send_payment_reminders(session: Session, notification_service: NotificationService | None = None) -> int:
    notification_service = notification_service or NotificationService()
    now = datetime.utcnow()
    target_date = now + timedelta(days=15)
    date_min = target_date - timedelta(days=1)
    date_max = target_date + timedelta(days=1)
    sent = 0

    raffles = session.exec(
        select(Raffle).where(
            Raffle.status == RaffleStatus.active,
            Raffle.draw_date >= date_min,
            Raffle.draw_date <= date_max,
        )
    ).all()
    for raffle in raffles:
        pending_reservations = session.exec(
            select(Reservation).where(
                Reservation.raffle_id == raffle.id,
                Reservation.status == ReservationStatus.pending,
                Reservation.reminder_sent_at.is_(None),
            )
        ).all()
        for reservation in pending_reservations:
            try:
                notification_service.send_whatsapp(
                    reservation.buyer_phone,
                    "payment_reminder",
                    {
                        "buyer_name": reservation.buyer_name,
                        "number": reservation.number,
                        "raffle_name": raffle.name,
                        "draw_date": raffle.draw_date.isoformat(),
                        "deadline": reservation.expires_at.isoformat(),
                    },
                )
                reservation.reminder_sent_at = now
                session.add(reservation)
                sent += 1
            except Exception as exc:
                logger.exception("Payment reminder error for reservation %s: %s", reservation.id, exc)
    session.commit()
    return sent


def register_winner(
    session: Session,
    raffle: Raffle,
    winner_number: int,
    notification_service: NotificationService | None = None,
) -> Raffle:
    if raffle.status != RaffleStatus.active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La rifa ya esta cerrada")
    if winner_number >= raffle.total_numbers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Numero ganador fuera de rango")

    winner_reservation = session.exec(
        select(Reservation).where(
            Reservation.raffle_id == raffle.id,
            Reservation.number == winner_number,
            Reservation.status == ReservationStatus.paid,
        )
    ).first()
    if winner_reservation is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El numero ganador no tiene una boleta pagada")

    raffle.status = RaffleStatus.closed
    raffle.winner_number = winner_number
    raffle.winner_registered_at = datetime.utcnow()
    session.add(raffle)
    session.commit()
    session.refresh(raffle)

    notification_service = notification_service or NotificationService()
    notification_service.send_whatsapp(
        winner_reservation.buyer_phone,
        "winner_notification",
        {
            "buyer_name": winner_reservation.buyer_name,
            "prize": raffle.prize_description,
            "organizer_phone": get_settings().organizer_phone,
        },
    )
    return raffle


def get_raffle_stats(session: Session, raffle: Raffle) -> RaffleStatsRead:
    expire_old_reservations(session, raffle.id or 0)
    reservations = session.exec(select(Reservation).where(Reservation.raffle_id == raffle.id)).all()
    paid = sum(1 for reservation in reservations if reservation.status == ReservationStatus.paid)
    reserved = sum(1 for reservation in reservations if reservation.status == ReservationStatus.pending)
    available = raffle.total_numbers - paid - reserved
    return RaffleStatsRead(
        total_raised=paid * raffle.ticket_price,
        numbers_sold=paid,
        numbers_reserved=reserved,
        numbers_available=available,
        pending_payments=reserved,
        percentage_sold=(paid / raffle.total_numbers) * 100 if raffle.total_numbers else 0,
    )


def get_raffle_buyers(session: Session, raffle: Raffle) -> list[BuyerRead]:
    reservations = session.exec(
        select(Reservation).where(Reservation.raffle_id == raffle.id).order_by(Reservation.created_at.desc())
    ).all()
    return [
        BuyerRead(
            name=reservation.buyer_name,
            phone=reservation.buyer_phone,
            email=reservation.buyer_email,
            number=reservation.number,
            payment_method=reservation.payment_method,
            status=reservation.status,
        )
        for reservation in reservations
    ]


def expire_all_old_reservations(session: Session) -> int:
    now = datetime.utcnow()
    expired = session.exec(
        select(Reservation).where(
            Reservation.status == ReservationStatus.pending,
            Reservation.expires_at <= now,
        )
    ).all()
    for reservation in expired:
        reservation.status = ReservationStatus.expired
        session.add(reservation)
    if expired:
        session.commit()
    return len(expired)
