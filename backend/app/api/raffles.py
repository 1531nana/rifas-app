from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import get_current_admin
from app.core.database import get_session
from app.models.domain import Admin, Raffle
from app.models.schemas import RaffleCreate, RaffleRead
from app.services.raffles import create_raffle

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
