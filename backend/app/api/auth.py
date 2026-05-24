from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.domain import Admin
from app.models.schemas import AdminCreate, AdminLogin, RefreshRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: AdminCreate, session: Session = Depends(get_session)) -> TokenResponse:
    existing = session.exec(select(Admin).where(Admin.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya esta registrado")
    admin = Admin(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return TokenResponse(
        access_token=create_access_token(str(admin.id)),
        refresh_token=create_refresh_token(str(admin.id)),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: AdminLogin, session: Session = Depends(get_session)) -> TokenResponse:
    admin = session.exec(select(Admin).where(Admin.email == payload.email)).first()
    if admin is None or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")
    return TokenResponse(
        access_token=create_access_token(str(admin.id)),
        refresh_token=create_refresh_token(str(admin.id)),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest) -> TokenResponse:
    subject = decode_refresh_token(payload.refresh_token)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido o expirado")
    return TokenResponse(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
    )
