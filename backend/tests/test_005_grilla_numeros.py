from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.database import create_db_and_tables, engine
from app.main import app
from app.models.domain import Reservation, ReservationStatus

create_db_and_tables()
client = TestClient(app)


def _register_and_create_raffle(total_numbers=50):
    email = f"admin-{uuid4().hex}@example.com"
    register = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Admin Test"},
    )
    assert register.status_code == 201
    token = register.json()["access_token"]

    create = client.post(
        "/raffles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Rifa Numeros",
            "lottery_type": "Loteria de Bogota",
            "total_numbers": total_numbers,
            "ticket_price": 10000,
            "prize_description": "Premio test",
            "draw_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        },
    )
    assert create.status_code == 201
    return create.json()


def test_numbers_endpoint_returns_all_states():
    raffle = _register_and_create_raffle(total_numbers=10)
    public_token = raffle["public_token"]

    response = client.get(f"/r/{public_token}/numbers")
    assert response.status_code == 200
    numbers = response.json()
    assert len(numbers) == 10
    statuses = {n["status"] for n in numbers}
    assert statuses <= {"available", "reserved", "sold"}
    assert all(n["status"] == "available" for n in numbers)


def test_numbers_endpoint_reflects_reservation():
    raffle = _register_and_create_raffle(total_numbers=20)
    public_token = raffle["public_token"]

    client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 5,
            "buyer_name": "Comprador Test",
            "buyer_phone": "+573001112233",
            "payment_method": "cash",
        },
    )

    response = client.get(f"/r/{public_token}/numbers")
    assert response.status_code == 200
    numbers = response.json()
    numero_5 = next(n for n in numbers if n["number"] == 5)
    assert numero_5["status"] == "reserved"


def test_numbers_endpoint_expired_reservation_returns_available():
    raffle = _register_and_create_raffle(total_numbers=20)
    public_token = raffle["public_token"]

    reserve = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 3,
            "buyer_name": "Comprador Expira",
            "buyer_phone": "+573009998877",
            "payment_method": "cash",
        },
    )
    assert reserve.status_code == 201

    with Session(engine) as session:
        reservation = session.exec(
            select(Reservation).where(Reservation.id == reserve.json()["id"])
        ).first()
        reservation.expires_at = datetime.utcnow() - timedelta(hours=1)
        session.add(reservation)
        session.commit()

    response = client.get(f"/r/{public_token}/numbers")
    assert response.status_code == 200
    numero_3 = next(n for n in response.json() if n["number"] == 3)
    assert numero_3["status"] == "available"


def test_numbers_endpoint_404_for_unknown_token():
    response = client.get("/r/token-inexistente-abc/numbers")
    assert response.status_code == 404
