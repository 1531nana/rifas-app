from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session, select

from app.api.deps import get_current_admin
from app.core.database import get_session
from app.models.domain import Admin, Raffle, Reservation
from app.models.schemas import RaffleCreate, RaffleDetailRead, RaffleRead, RaffleUpdate, ReservationRead
from app.services.raffles import (
    confirm_cash_payment,
    create_raffle,
    get_owned_raffle,
    get_raffle_detail,
    update_raffle,
    upload_prize_image,
)

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


@router.patch("/{raffle_id}", response_model=RaffleRead)
def update_raffle_endpoint(
    raffle_id: int,
    payload: RaffleUpdate,
    current_admin: Admin = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> Raffle:
    raffle = get_owned_raffle(session, current_admin.id or 0, raffle_id)
    return update_raffle(session, raffle, payload)


@router.post("/{raffle_id}/image", response_model=RaffleRead)
def upload_raffle_image_endpoint(
    raffle_id: int,
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin),
    session: Session = Depends(get_session),
) -> Raffle:
    raffle = get_owned_raffle(session, current_admin.id or 0, raffle_id)
    return upload_prize_image(session, raffle, file)


@router.patch("/reservations/{reservation_id}/confirm-cash", response_model=ReservationRead)
def confirm_cash_payment_by_reservation_endpoint(
    reservation_id: int,
    current_admin: Admin = Depends(get_current_admin),
    session: Session = Depends(get_session),
):
    # First get the reservation to verify it exists and get its raffle_id
    reservation = session.exec(
        select(Reservation).where(Reservation.id == reservation_id)
    ).first()

    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")

    # Then verify the admin owns the raffle associated with this reservation
    raffle = session.exec(
        select(Raffle).where(
            Raffle.id == reservation.raffle_id,
            Raffle.admin_id == current_admin.id
        )
    ).first()

    if not raffle:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para confirmar este pago")

    return confirm_cash_payment(session, raffle, reservation_id)


@router.post("/{raffle_id}/reservations/{reservation_id}/confirm-cash", response_model=ReservationRead)
def confirm_cash_payment_endpoint(
    raffle_id: int,
    reservation_id: int,
    current_admin: Admin = Depends(get_current_admin),
    session: Session = Depends(get_session),
):
    raffle = get_owned_raffle(session, current_admin.id or 0, raffle_id)
    return confirm_cash_payment(session, raffle, reservation_id)
