from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import create_db_and_tables
from app.main import app

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
            "name": "Rifa Reserva",
            "lottery_type": "Loteria de Bogota",
            "total_numbers": total_numbers,
            "ticket_price": 10000,
            "prize_description": "Premio test",
            "draw_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        },
    )
    assert create.status_code == 201
    return create.json(), token


def test_confirm_cash_payment_by_owner():
    # Create raffle and get admin token
    raffle, owner_token = _register_and_create_raffle()
    public_token = raffle["public_token"]

    # Make a cash reservation as a buyer
    buyer_response = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 10,
            "buyer_name": "Juan Perez",
            "buyer_phone": "+573001112233",
            "payment_method": "cash",
        },
    )
    assert buyer_response.status_code == 201
    reservation_id = buyer_response.json()["id"]

    # Owner confirms the cash payment
    confirm_response = client.patch(
        f"/raffles/reservations/{reservation_id}/confirm-cash",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert confirm_response.status_code == 200
    data = confirm_response.json()
    assert data["status"] == "paid"
    assert data["payment_method"] == "cash"
    assert "paid_at" in data
    assert data["paid_at"] is not None


def test_confirm_cash_payment_by_non_owner_fails():
    # Create raffle and get owner token
    raffle, owner_token = _register_and_create_raffle()
    public_token = raffle["public_token"]

    # Create another admin (non-owner)
    other_email = f"admin-{uuid4().hex}@example.com"
    other_register = client.post(
        "/auth/register",
        json={"email": other_email, "password": "supersecret", "full_name": "Other Admin"},
    )
    assert other_register.status_code == 201
    other_token = other_register.json()["access_token"]

    # Make a cash reservation
    buyer_response = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 10,
            "buyer_name": "Juan Perez",
            "buyer_phone": "+573001112233",
            "payment_method": "cash",
        },
    )
    assert buyer_response.status_code == 201
    reservation_id = buyer_response.json()["id"]

    # Non-owner tries to confirm -> should fail
    confirm_response = client.patch(
        f"/raffles/reservations/{reservation_id}/confirm-cash",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert confirm_response.status_code == 403  # Forbidden


def test_confirm_cash_payment_only_for_cash():
    raffle, owner_token = _register_and_create_raffle()
    public_token = raffle["public_token"]

    # Make a card reservation
    buyer_response = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 10,
            "buyer_name": "Juan Perez",
            "buyer_phone": "+573001112233",
            "payment_method": "card",
        },
    )
    assert buyer_response.status_code == 201
    reservation_id = buyer_response.json()["id"]

    # Try to confirm as cash -> should fail
    confirm_response = client.patch(
        f"/raffles/reservations/{reservation_id}/confirm-cash",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert confirm_response.status_code == 409  # Conflict