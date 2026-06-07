from datetime import datetime, timedelta
import logging
from pathlib import Path
from secrets import token_urlsafe

from fastapi import HTTPException, UploadFile, status
import httpx
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.database import engine
from app.models.domain import PaymentMethod, Raffle, RaffleStatus, Reservation, ReservationStatus
from app.models.schemas import BuyerRead, NumberState, RaffleCreate, RaffleDetailRead, RaffleStatsRead, RaffleUpdate, RegisterWinnerRequest, ReservationCreate
from app.services.notifications import send_whatsapp

logger = logging.getLogger(__name__)
MAX_IMAGE_BYTES = 5 * 1024 * 1024
IMAGE_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


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


def has_active_reservations(session: Session, raffle_id: int) -> bool:
    active = session.exec(
        select(Reservation).where(
            Reservation.raffle_id == raffle_id,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.paid]),
        )
    ).first()
    return active is not None


def update_raffle(session: Session, raffle: Raffle, payload: RaffleUpdate) -> Raffle:
    if has_active_reservations(session, raffle.id or 0):
        if payload.total_numbers is not None or payload.ticket_price is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede cambiar el precio ni la cantidad de numeros porque hay reservas activas",
            )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(raffle, field, value)
    session.add(raffle)
    session.commit()
    session.refresh(raffle)
    return raffle


def upload_prize_image(session: Session, raffle: Raffle, file: UploadFile) -> Raffle:
    extension = IMAGE_CONTENT_TYPES.get(file.content_type or "")
    if extension is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se aceptan imagenes JPG, PNG o WebP")

    content = file.file.read(MAX_IMAGE_BYTES + 1)
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen esta vacia")
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="La imagen supera 5MB")

    settings = get_settings()
    filename = f"raffle-{raffle.id}-{token_urlsafe(8)}{extension}"
    if settings.cloudinary_cloud_name and settings.cloudinary_upload_preset:
        raffle.prize_image_url = upload_to_cloudinary(settings, filename, content, file.content_type or "application/octet-stream")
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


def upload_to_cloudinary(settings, filename: str, content: bytes, content_type: str) -> str:
    public_id = filename.rsplit(".", 1)[0]
    try:
        response = httpx.post(
            f"https://api.cloudinary.com/v1_1/{settings.cloudinary_cloud_name}/image/upload",
            data={"upload_preset": settings.cloudinary_upload_preset, "public_id": public_id},
            files={"file": (filename, content, content_type)},
            timeout=20,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="No se pudo subir la imagen") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Cloudinary rechazo la imagen")

    image_url = response.json().get("secure_url") or response.json().get("url")
    if not image_url:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Cloudinary no retorno URL de imagen")
    return image_url


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


def _reserva_vigente(reservation: Reservation, ahora: datetime) -> bool:
    """Función pura: determina si una reserva ocupa un número sin tocar la BD."""
    if reservation.status == ReservationStatus.paid:
        return True
    if reservation.status == ReservationStatus.pending:
        return reservation.expires_at > ahora
    return False


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
    ahora = datetime.utcnow()
    reservations = session.exec(
        select(Reservation).where(
            Reservation.raffle_id == raffle.id,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.paid]),
        )
    ).all()
    activo_por_numero = {
        r.number: r.status
        for r in reservations
        if _reserva_vigente(r, ahora)
    }

    states: list[NumberState] = []
    for number in range(raffle.total_numbers):
        reservation_status = activo_por_numero.get(number)
        if reservation_status == ReservationStatus.paid:
            status_value = "sold"
        elif reservation_status == ReservationStatus.pending:
            status_value = "reserved"
        else:
            status_value = "available"
        states.append(NumberState(number=number, status=status_value))
    return states


def get_raffle_detail(session: Session, raffle: Raffle) -> RaffleDetailRead:
    ahora = datetime.utcnow()
    reservations = list(
        session.exec(
            select(Reservation)
            .where(Reservation.raffle_id == raffle.id)
            .order_by(Reservation.created_at.desc())
        ).all()
    )
    active = [r for r in reservations if _reserva_vigente(r, ahora)]
    sold_count = sum(1 for r in active if r.status == ReservationStatus.paid)
    reserved_count = sum(1 for r in active if r.status == ReservationStatus.pending)

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

    ahora = datetime.utcnow()
    candidatas = session.exec(
        select(Reservation).where(
            Reservation.raffle_id == raffle.id,
            Reservation.number == payload.number,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.paid]),
        )
    ).all()
    if any(_reserva_vigente(r, ahora) for r in candidatas):
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
    send_payment_confirmation(reservation, raffle)
    return reservation


def send_payment_confirmation(reservation: Reservation, raffle: Raffle) -> bool:
    settings = get_settings()
    return send_whatsapp(
        reservation.buyer_phone,
        settings.meta_template_payment_confirmation,
        {
            "buyer_name": reservation.buyer_name,
            "number": reservation.number,
            "raffle_name": raffle.name,
            "draw_date": raffle.draw_date.isoformat(),
        },
    )


def get_raffle_stats(session: Session, raffle: Raffle) -> RaffleStatsRead:
    ahora = datetime.utcnow()
    reservations = session.exec(
        select(Reservation).where(
            Reservation.raffle_id == raffle.id,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.paid]),
        )
    ).all()
    active = [r for r in reservations if _reserva_vigente(r, ahora)]
    sold = sum(1 for r in active if r.status == ReservationStatus.paid)
    pending = sum(1 for r in active if r.status == ReservationStatus.pending)
    return RaffleStatsRead(
        total_numbers=raffle.total_numbers,
        sold_count=sold,
        reserved_count=pending,
        available_count=raffle.total_numbers - sold - pending,
        paid_total=sold * raffle.ticket_price,
        pending_payments=pending,
    )


def get_raffle_buyers(session: Session, raffle: Raffle) -> list[BuyerRead]:
    reservations = session.exec(
        select(Reservation)
        .where(Reservation.raffle_id == raffle.id)
        .order_by(Reservation.created_at.desc())
    ).all()
    return [BuyerRead.model_validate(r) for r in reservations]


def run_expiration_job() -> None:
    try:
        with Session(engine) as session:
            active_raffles = session.exec(
                select(Raffle).where(Raffle.status == RaffleStatus.active)
            ).all()
            for raffle in active_raffles:
                expire_old_reservations(session, raffle.id or 0)
    except Exception:
        logger.exception("Error ejecutando job de expiracion de reservas")
