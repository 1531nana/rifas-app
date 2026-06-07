from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import create_db_and_tables
from app.main import app

create_db_and_tables()
client = TestClient(app)


def _setup_raffle_with_reservations():
    email = f"admin-{uuid4().hex}@example.com"
    token = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Admin Stats"},
    ).json()["access_token"]

    raffle = client.post(
        "/raffles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Rifa Estadisticas",
            "lottery_type": "Chance",
            "total_numbers": 20,
            "ticket_price": 10000,
            "prize_description": "Televisor 55 pulgadas",
            "draw_date": (datetime.utcnow() + timedelta(days=20)).isoformat(),
        },
    ).json()

    # reserva pendiente
    client.post(
        f"/r/{raffle['public_token']}/reserve",
        json={
            "number": 0,
            "buyer_name": "Comprador Pendiente",
            "buyer_phone": "+573001000001",
            "payment_method": "cash",
        },
    )

    # reserva pagada (efectivo confirmado)
    res = client.post(
        f"/r/{raffle['public_token']}/reserve",
        json={
            "number": 1,
            "buyer_name": "Comprador Pagado",
            "buyer_phone": "+573001000002",
            "buyer_email": "pagado@test.com",
            "payment_method": "cash",
        },
    )
    reservation_id = res.json()["id"]
    client.patch(
        f"/reservations/{reservation_id}/confirm-cash",
        headers={"Authorization": f"Bearer {token}"},
    )

    return token, raffle


def test_get_stats_retorna_totales_correctos():
    token, raffle = _setup_raffle_with_reservations()

    resp = client.get(
        f"/raffles/{raffle['id']}/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_numbers"] == 20
    assert data["sold_count"] == 1
    assert data["reserved_count"] == 1
    assert data["available_count"] == 18
    assert data["paid_total"] == 10000
    assert data["pending_payments"] == 1


def test_get_stats_solo_accesible_por_dueno():
    _, raffle = _setup_raffle_with_reservations()
    otro_token = client.post(
        "/auth/register",
        json={
            "email": f"otro-{uuid4().hex}@example.com",
            "password": "supersecret",
            "full_name": "Otro Admin",
        },
    ).json()["access_token"]

    resp = client.get(
        f"/raffles/{raffle['id']}/stats",
        headers={"Authorization": f"Bearer {otro_token}"},
    )
    assert resp.status_code == 404


def test_get_buyers_retorna_lista_de_compradores():
    token, raffle = _setup_raffle_with_reservations()

    resp = client.get(
        f"/raffles/{raffle['id']}/buyers",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    buyers = resp.json()
    assert len(buyers) == 2

    nombres = {b["buyer_name"] for b in buyers}
    assert "Comprador Pendiente" in nombres
    assert "Comprador Pagado" in nombres

    pagado = next(b for b in buyers if b["buyer_name"] == "Comprador Pagado")
    assert pagado["status"] == "paid"
    assert pagado["number"] == 1
    assert pagado["payment_method"] == "cash"


def test_get_buyers_solo_accesible_por_dueno():
    _, raffle = _setup_raffle_with_reservations()
    otro_token = client.post(
        "/auth/register",
        json={
            "email": f"otro2-{uuid4().hex}@example.com",
            "password": "supersecret",
            "full_name": "Otro Admin 2",
        },
    ).json()["access_token"]

    resp = client.get(
        f"/raffles/{raffle['id']}/buyers",
        headers={"Authorization": f"Bearer {otro_token}"},
    )
    assert resp.status_code == 404
