import hashlib
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.database import create_db_and_tables
from app.main import app

create_db_and_tables()
client = TestClient(app)

EVENTS_KEY = get_settings().wompi_events_key

# Propiedades que Wompi envía en el webhook (relativas a payload["data"])
WEBHOOK_PROPERTIES = [
    "transaction.id",
    "transaction.status",
    "transaction.amount_in_cents",
    "transaction.currency",
    "transaction.payment_method_type",
]


def _wompi_checksum(transaction: dict, timestamp: int, events_key: str) -> str:
    """
    Replica el algoritmo oficial de Wompi:
    SHA256(prop_values + timestamp + events_key)
    Los paths son relativos a payload["data"].
    """
    data = {"transaction": transaction}
    concatenated = ""
    for prop in WEBHOOK_PROPERTIES:
        value = data
        for key in prop.split("."):
            value = value[key]
        concatenated += str(value)
    concatenated += str(timestamp)
    concatenated += events_key
    return hashlib.sha256(concatenated.encode()).hexdigest()


def _crear_raffle_y_reserva_digital():
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
            "name": "Rifa Pago Digital",
            "lottery_type": "Loteria de Bogota",
            "total_numbers": 50,
            "ticket_price": 20000,
            "prize_description": "Premio test",
            "draw_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        },
    )
    assert create.status_code == 201
    public_token = create.json()["public_token"]

    reserve = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 5,
            "buyer_name": "Comprador Digital",
            "buyer_phone": "+573001112233",
            "payment_method": "card",
        },
    )
    assert reserve.status_code == 201
    return public_token, reserve.json()["id"]


def _webhook_payload(reservation_id: int, estado: str) -> dict:
    timestamp = 1610641025
    transaction = {
        "id": f"wompi-tx-{uuid4().hex[:8]}",
        "status": estado,
        "amount_in_cents": 2000000,
        "currency": "COP",
        "payment_method_type": "CARD",
        "reference": f"rifas-reserva-{reservation_id}",
    }
    checksum = _wompi_checksum(transaction, timestamp, EVENTS_KEY)
    return {
        "event": "transaction.updated",
        "data": {"transaction": transaction},
        "environment": "test",
        "timestamp": timestamp,
        "sent_at": "2021-01-14T19:57:05.000Z",
        "signature": {"properties": WEBHOOK_PROPERTIES, "checksum": checksum},
    }


def test_checkout_retorna_url_de_wompi():
    public_token, reservation_id = _crear_raffle_y_reserva_digital()

    response = client.post(f"/r/{public_token}/reservations/{reservation_id}/checkout")
    assert response.status_code == 200
    data = response.json()
    assert "checkout_url" in data
    assert "checkout.wompi.co" in data["checkout_url"]
    assert "referencia" in data


def test_checkout_efectivo_retorna_400():
    email = f"admin-{uuid4().hex}@example.com"
    register = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Admin"},
    )
    token = register.json()["access_token"]
    create = client.post(
        "/raffles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Rifa Efectivo",
            "lottery_type": "Loteria",
            "total_numbers": 50,
            "ticket_price": 10000,
            "prize_description": "Premio",
            "draw_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        },
    )
    public_token = create.json()["public_token"]
    reserve = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 3,
            "buyer_name": "Comprador Efectivo",
            "buyer_phone": "+573009998877",
            "payment_method": "cash",
        },
    )
    reservation_id = reserve.json()["id"]

    response = client.post(f"/r/{public_token}/reservations/{reservation_id}/checkout")
    assert response.status_code == 400


def test_webhook_approved_marca_reserva_pagada():
    public_token, reservation_id = _crear_raffle_y_reserva_digital()

    response = client.post("/webhooks/wompi", json=_webhook_payload(reservation_id, "APPROVED"))
    assert response.status_code == 200

    numeros = client.get(f"/r/{public_token}/numbers")
    numero_5 = next(n for n in numeros.json() if n["number"] == 5)
    assert numero_5["status"] == "sold"


def test_webhook_declined_libera_numero():
    public_token, reservation_id = _crear_raffle_y_reserva_digital()

    response = client.post("/webhooks/wompi", json=_webhook_payload(reservation_id, "DECLINED"))
    assert response.status_code == 200

    numeros = client.get(f"/r/{public_token}/numbers")
    numero_5 = next(n for n in numeros.json() if n["number"] == 5)
    assert numero_5["status"] == "available"


def test_webhook_voided_libera_numero():
    public_token, reservation_id = _crear_raffle_y_reserva_digital()

    response = client.post("/webhooks/wompi", json=_webhook_payload(reservation_id, "VOIDED"))
    assert response.status_code == 200

    numeros = client.get(f"/r/{public_token}/numbers")
    numero_5 = next(n for n in numeros.json() if n["number"] == 5)
    assert numero_5["status"] == "available"


def test_webhook_firma_invalida_retorna_400():
    payload = _webhook_payload(99, "APPROVED")
    payload["signature"]["checksum"] = "firma-incorrecta"

    response = client.post("/webhooks/wompi", json=payload)
    assert response.status_code == 400
