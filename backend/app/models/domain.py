from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class RaffleStatus(str, Enum):
    active = "active"
    closed = "closed"


class ReservationStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    expired = "expired"
    cancelled = "cancelled"


class PaymentMethod(str, Enum):
    card = "card"
    pse = "pse"
    cash = "cash"


class Admin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(index=True, unique=True)
    password_hash: str
    full_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Raffle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    admin_id: int = Field(foreign_key="admin.id", index=True)
    name: str
    lottery_type: str
    total_numbers: int
    ticket_price: int
    prize_description: str
    draw_date: datetime
    prize_image_url: Optional[str] = None
    public_token: str = Field(index=True, unique=True)
    status: RaffleStatus = Field(default=RaffleStatus.active)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    raffle_id: int = Field(foreign_key="raffle.id", index=True)
    number: int = Field(index=True)
    buyer_name: str
    buyer_phone: str
    buyer_email: Optional[EmailStr] = None
    payment_method: PaymentMethod
    status: ReservationStatus = Field(default=ReservationStatus.pending, index=True)
    expires_at: datetime
    paid_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
