from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import create_db_and_tables
from app.main import app

create_db_and_tables()
client = TestClient(app)


def _setup_raffle_with_paid_number(number: int = 5):
    email = f"admin-{uuid4().hex}@example.com"
    token = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Admin Ganador"},
    ).json()["access_token"]

    raffle = client.post(
        "/raffles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Rifa Ganador Test",
            "lottery_type": "Loteria de Medellin",
            "total_numbers": 20,
            "ticket_price": 15000,
            "prize_description": "Nevera doble puerta",
            "draw_date": (datetime.utcnow() + timedelta(days=10)).isoformat(),
        },
    ).json()

    res = client.post(
        f"/r/{raffle['public_token']}/reserve",
        json={
            "number": number,
            "buyer_name": "Comprador Ganador",
            "buyer_phone": "+573009990001",
            "payment_method": "cash",
        },
    )
    reservation_id = res.json()["id"]
    client.patch(
        f"/reservations/{reservation_id}/confirm-cash",
        headers={"Authorization": f"Bearer {token}"},
    )
    return token, raffle


def test_registrar_ganador_cierra_rifa(monkeypatch):
    monkeypatch.setattr("app.services.ganador.send_whatsapp", lambda *a, **kw: True)
    token, raffle = _setup_raffle_with_paid_number(number=5)

    resp = client.post(
        f"/raffles/{raffle['id']}/winner",
        headers={"Authorization": f"Bearer {token}"},
        json={"number": 5},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "closed"
    assert data["winner_number"] == 5


def test_registrar_ganador_notifica_comprador(monkeypatch):
    calls = []

    def fake_send(phone, template, params):
        calls.append({"phone": phone, "template": template, "params": params})
        return True

    monkeypatch.setattr("app.services.ganador.send_whatsapp", fake_send)
    token, raffle = _setup_raffle_with_paid_number(number=3)

    client.post(
        f"/raffles/{raffle['id']}/winner",
        headers={"Authorization": f"Bearer {token}"},
        json={"number": 3},
    )

    assert len(calls) == 1
    assert calls[0]["phone"] == "+573009990001"
    assert calls[0]["template"] == "winner_notification"
    assert calls[0]["params"]["buyer_name"] == "Comprador Ganador"
    assert calls[0]["params"]["prize_description"] == "Nevera doble puerta"


def test_registrar_ganador_rechaza_numero_sin_pago(monkeypatch):
    monkeypatch.setattr("app.services.ganador.send_whatsapp", lambda *a, **kw: True)
    token, raffle = _setup_raffle_with_paid_number(number=5)

    resp = client.post(
        f"/raffles/{raffle['id']}/winner",
        headers={"Authorization": f"Bearer {token}"},
        json={"number": 7},
    )
    assert resp.status_code == 409


def test_registrar_ganador_rechaza_rifa_ya_cerrada(monkeypatch):
    monkeypatch.setattr("app.services.ganador.send_whatsapp", lambda *a, **kw: True)
    token, raffle = _setup_raffle_with_paid_number(number=5)

    client.post(
        f"/raffles/{raffle['id']}/winner",
        headers={"Authorization": f"Bearer {token}"},
        json={"number": 5},
    )
    resp = client.post(
        f"/raffles/{raffle['id']}/winner",
        headers={"Authorization": f"Bearer {token}"},
        json={"number": 5},
    )
    assert resp.status_code == 409


def test_rifa_cerrada_rechaza_nuevas_reservas(monkeypatch):
    monkeypatch.setattr("app.services.ganador.send_whatsapp", lambda *a, **kw: True)
    token, raffle = _setup_raffle_with_paid_number(number=5)

    client.post(
        f"/raffles/{raffle['id']}/winner",
        headers={"Authorization": f"Bearer {token}"},
        json={"number": 5},
    )
    resp = client.post(
        f"/r/{raffle['public_token']}/reserve",
        json={
            "number": 10,
            "buyer_name": "Comprador Tardio",
            "buyer_phone": "+573001112222",
            "payment_method": "cash",
        },
    )
    assert resp.status_code == 409


def test_vista_publica_muestra_ganador(monkeypatch):
    monkeypatch.setattr("app.services.ganador.send_whatsapp", lambda *a, **kw: True)
    token, raffle = _setup_raffle_with_paid_number(number=2)

    client.post(
        f"/raffles/{raffle['id']}/winner",
        headers={"Authorization": f"Bearer {token}"},
        json={"number": 2},
    )
    public = client.get(f"/public/raffles/{raffle['public_token']}")
    assert public.status_code == 200
    assert public.json()["winner_number"] == 2


def test_registrar_ganador_solo_por_dueno(monkeypatch):
    monkeypatch.setattr("app.services.ganador.send_whatsapp", lambda *a, **kw: True)
    token, raffle = _setup_raffle_with_paid_number(number=5)

    otro_token = client.post(
        "/auth/register",
        json={
            "email": f"otro-{uuid4().hex}@example.com",
            "password": "supersecret",
            "full_name": "Otro Admin",
        },
    ).json()["access_token"]

    resp = client.post(
        f"/raffles/{raffle['id']}/winner",
        headers={"Authorization": f"Bearer {otro_token}"},
        json={"number": 5},
    )
    assert resp.status_code == 404
