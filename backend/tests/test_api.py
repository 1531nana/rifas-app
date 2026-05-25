from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.database import create_db_and_tables, engine
from app.main import app
from app.models.domain import Raffle, Reservation, ReservationStatus

create_db_and_tables()
client = TestClient(app)


def test_admin_can_create_raffle_and_buyer_can_reserve_number():
    email = f"admin-{uuid4().hex}@example.com"
    register = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Admin Demo"},
    )
    assert register.status_code == 201
    token = register.json()["access_token"]

    create = client.post(
        "/raffles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Rifa Moto Mayo",
            "lottery_type": "Loteria de Bogota",
            "total_numbers": 100,
            "ticket_price": 25000,
            "prize_description": "Moto nueva 125cc",
            "draw_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        },
    )
    assert create.status_code == 201
    public_token = create.json()["public_token"]

    public = client.get(f"/r/{public_token}")
    assert public.status_code == 200
    assert public.json()["numbers"][7]["status"] == "available"

    reserve = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 7,
            "buyer_name": "Comprador Demo",
            "buyer_phone": "+573001112233",
            "buyer_email": "buyer@example.com",
            "payment_method": "cash",
        },
    )
    assert reserve.status_code == 201
    assert reserve.json()["number"] == 7

    duplicate = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 7,
            "buyer_name": "Otro Comprador",
            "buyer_phone": "+573004445566",
            "payment_method": "cash",
        },
    )
    assert duplicate.status_code == 409

    detail = client.get(f"/raffles/{create.json()['id']}", headers={"Authorization": f"Bearer {token}"})
    assert detail.status_code == 200
    assert detail.json()["reserved_count"] == 1
    assert detail.json()["reservations"][0]["buyer_name"] == "Comprador Demo"

    reservation_id = reserve.json()["id"]
    confirmed = client.patch(
        f"/raffles/reservations/{reservation_id}/confirm-cash",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "paid"


def test_refresh_token_flow():
    email = f"admin-{uuid4().hex}@example.com"
    register = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Admin Demo"},
    )
    assert register.status_code == 201
    data = register.json()
    assert "access_token" in data
    assert "refresh_token" in data

    refresh = client.post(
        "/auth/refresh",
        json={"refresh_token": data["refresh_token"]},
    )
    assert refresh.status_code == 200
    new_data = refresh.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data

    bad_refresh = client.post(
        "/auth/refresh",
        json={"refresh_token": "invalid-token"},
    )
    assert bad_refresh.status_code == 401


def test_expiration_job_marks_expired_reservations():
    email = f"admin-{uuid4().hex}@example.com"
    register = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Admin Demo"},
    )
    assert register.status_code == 201
    token = register.json()["access_token"]

    create = client.post(
        "/raffles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Rifa Expiracion",
            "lottery_type": "Loteria de Medellin",
            "total_numbers": 50,
            "ticket_price": 10000,
            "prize_description": "Premio prueba",
            "draw_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        },
    )
    assert create.status_code == 201
    raffle_id = create.json()["id"]
    public_token = create.json()["public_token"]

    reserve = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 12,
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

    from app.services.raffles import run_expiration_job
    run_expiration_job()

    public = client.get(f"/r/{public_token}")
    assert public.status_code == 200
    number_12 = [n for n in public.json()["numbers"] if n["number"] == 12][0]
    assert number_12["status"] == "available"

    with Session(engine) as session:
        reservation = session.exec(
            select(Reservation).where(Reservation.id == reserve.json()["id"])
        ).first()
        assert reservation.status == ReservationStatus.expired


def test_admin_edit_raffle():
    email = f"admin-edit-{uuid4().hex}@example.com"
    register = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Admin Edit"},
    )
    assert register.status_code == 201
    token = register.json()["access_token"]

    create = client.post(
        "/raffles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Rifa Original",
            "lottery_type": "Loteria de Bogota",
            "total_numbers": 100,
            "ticket_price": 25000,
            "prize_description": "Premio original",
            "draw_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        },
    )
    assert create.status_code == 201
    raffle_id = create.json()["id"]

    patch = client.patch(
        f"/raffles/{raffle_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Rifa Editada",
            "lottery_type": "Loteria de Medellin",
            "draw_date": (datetime.utcnow() + timedelta(days=60)).isoformat(),
        },
    )
    assert patch.status_code == 200
    assert patch.json()["name"] == "Rifa Editada"
    assert patch.json()["lottery_type"] == "Loteria de Medellin"
    assert patch.json()["total_numbers"] == 100
    assert patch.json()["ticket_price"] == 25000


def test_admin_cannot_change_price_if_reservations_exist():
    email = f"admin-price-{uuid4().hex}@example.com"
    register = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Admin Price"},
    )
    assert register.status_code == 201
    token = register.json()["access_token"]

    create = client.post(
        "/raffles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Rifa Precio Fijo",
            "lottery_type": "Loteria de Bogota",
            "total_numbers": 50,
            "ticket_price": 10000,
            "prize_description": "Premio con precio fijo",
            "draw_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        },
    )
    assert create.status_code == 201
    raffle_id = create.json()["id"]
    public_token = create.json()["public_token"]

    reserve = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 5,
            "buyer_name": "Comprador",
            "buyer_phone": "+573001112233",
            "payment_method": "cash",
        },
    )
    assert reserve.status_code == 201

    patch_price = client.patch(
        f"/raffles/{raffle_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"ticket_price": 20000},
    )
    assert patch_price.status_code == 409

    patch_numbers = client.patch(
        f"/raffles/{raffle_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"total_numbers": 200},
    )
    assert patch_numbers.status_code == 409

    patch_ok = client.patch(
        f"/raffles/{raffle_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"prize_description": "Descripcion actualizada"},
    )
    assert patch_ok.status_code == 200
    assert patch_ok.json()["prize_description"] == "Descripcion actualizada"


def test_admin_cannot_edit_other_admin_raffle():
    email_a = f"admin-a-{uuid4().hex}@example.com"
    email_b = f"admin-b-{uuid4().hex}@example.com"

    register_a = client.post(
        "/auth/register",
        json={"email": email_a, "password": "supersecret", "full_name": "Admin A"},
    )
    assert register_a.status_code == 201
    token_a = register_a.json()["access_token"]

    register_b = client.post(
        "/auth/register",
        json={"email": email_b, "password": "supersecret", "full_name": "Admin B"},
    )
    assert register_b.status_code == 201
    token_b = register_b.json()["access_token"]

    create = client.post(
        "/raffles",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "name": "Rifa de Admin A",
            "lottery_type": "Loteria",
            "total_numbers": 100,
            "ticket_price": 10000,
            "prize_description": "Premio de Admin A",
            "draw_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        },
    )
    assert create.status_code == 201
    raffle_id = create.json()["id"]

    patch = client.patch(
        f"/raffles/{raffle_id}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"name": "Hackeado"},
    )
    assert patch.status_code == 404
