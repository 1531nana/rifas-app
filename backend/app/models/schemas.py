from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.domain import PaymentMethod, RaffleStatus, ReservationStatus
from app.models.validators import validate_phone


class AdminCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=120)


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class RaffleCreate(BaseModel):
    name: str = Field(min_length=3, max_length=160)
    lottery_type: str = Field(min_length=2, max_length=80)
    total_numbers: int = Field(ge=10, le=10000)
    ticket_price: int = Field(gt=0)
    prize_description: str = Field(min_length=5)
    draw_date: datetime
    prize_image_url: str | None = None


class RaffleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    lottery_type: str
    total_numbers: int
    ticket_price: int
    prize_description: str
    draw_date: datetime
    prize_image_url: str | None
    public_token: str
    status: RaffleStatus


class NumberState(BaseModel):
    number: int
    status: str


class PublicRaffleRead(RaffleRead):
    numbers: list[NumberState]


class ReservationCreate(BaseModel):
    number: int = Field(ge=0)
    buyer_name: str = Field(min_length=3, max_length=120)
    buyer_phone: str = Field(min_length=7, max_length=30)
    buyer_email: EmailStr | None = None
    payment_method: PaymentMethod

    @field_validator("buyer_phone")
    @classmethod
    def phone_formato_internacional(cls, v: str) -> str:
        return validate_phone(v)


class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    raffle_id: int
    number: int
    buyer_name: str
    buyer_phone: str
    buyer_email: EmailStr | None
    payment_method: PaymentMethod
    status: ReservationStatus
    expires_at: datetime
    paid_at: datetime | None = None


class RaffleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=160)
    lottery_type: str | None = Field(default=None, min_length=2, max_length=80)
    total_numbers: int | None = Field(default=None, ge=10, le=10000)
    ticket_price: int | None = Field(default=None, gt=0)
    prize_description: str | None = Field(default=None, min_length=5)
    draw_date: datetime | None = None
    prize_image_url: str | None = None


class RaffleStatsRead(BaseModel):
    total_numbers: int
    sold_count: int
    reserved_count: int
    available_count: int
    paid_total: int
    pending_payments: int


class BuyerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: int
    buyer_name: str
    buyer_phone: str
    buyer_email: EmailStr | None
    payment_method: PaymentMethod
    status: ReservationStatus
    paid_at: datetime | None = None


class RaffleDetailRead(RaffleRead):
    sold_count: int
    reserved_count: int
    available_count: int
    paid_total: int
    reservations: list[ReservationRead]
