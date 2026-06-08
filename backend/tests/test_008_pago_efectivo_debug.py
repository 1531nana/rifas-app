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


def test_debug_reservation_creation():
    # Create raffle and get admin token
    raffle, owner_token = _register_and_create_raffle()
    public_token = raffle["public_token"]
    print(f"Raffle ID: {raffle['id']}")
    print(f"Public token: {public_token}")

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
    print(f"Buyer response status: {buyer_response.status_code}")
    print(f"Buyer response: {buyer_response.json()}")
    assert buyer_response.status_code == 201
    reservation_id = buyer_response.json()["id"]
    print(f"Reservation ID: {reservation_id}")

    # Try to get the reservation directly
    get_resp = client.get(
        f"/reservations/{reservation_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    print(f"Get reservation status: {get_resp.status_code}")
    if get_resp.status_code != 200:
        print(f"Get reservation response: {get_resp.text}")
    
    # Owner confirms the cash payment
    confirm_response = client.patch(
        f"/reservations/{reservation_id}/confirm-cash",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    print(f"Confirm response status: {confirm_response.status_code}")
    print(f"Confirm response: {confirm_response.text}")