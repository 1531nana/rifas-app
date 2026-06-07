from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.database import create_db_and_tables, engine
from app.main import app
from app.models.domain import Reservation
from app.services.recordatorio import send_payment_reminders

create_db_and_tables()
client = TestClient(app)


def _setup_raffle_con_reserva_pendiente(dias_para_sorteo: int = 15):
    email = f"admin-{uuid4().hex}@example.com"
    token = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Admin Recordatorio"},
    ).json()["access_token"]

    raffle = client.post(
        "/raffles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Rifa Recordatorio",
            "lottery_type": "Baloto",
            "total_numbers": 20,
            "ticket_price": 5000,
            "prize_description": "Bicicleta electrica",
            "draw_date": (datetime.utcnow() + timedelta(days=dias_para_sorteo)).isoformat(),
        },
    ).json()

    res = client.post(
        f"/r/{raffle['public_token']}/reserve",
        json={
            "number": 7,
            "buyer_name": "Comprador Recordatorio",
            "buyer_phone": "+573002223344",
            "payment_method": "cash",
        },
    )
    return token, raffle, res.json()["id"]


def test_job_envia_whatsapp_a_reservas_pendientes_en_15_dias(monkeypatch):
    calls = []

    def fake_send(phone, template, params):
        calls.append({"phone": phone, "template": template, "params": params})
        return True

    monkeypatch.setattr("app.services.recordatorio.send_whatsapp", fake_send)
    _, _, reservation_id = _setup_raffle_con_reserva_pendiente(dias_para_sorteo=15)

    send_payment_reminders()

    assert len(calls) >= 1
    llamada = next((c for c in calls if c["phone"] == "+573002223344"), None)
    assert llamada is not None
    assert llamada["template"] == "payment_reminder"
    assert llamada["params"]["buyer_name"] == "Comprador Recordatorio"
    assert llamada["params"]["number"] == 7


def test_job_marca_reminder_sent_at(monkeypatch):
    monkeypatch.setattr("app.services.recordatorio.send_whatsapp", lambda *a, **kw: True)
    _, _, reservation_id = _setup_raffle_con_reserva_pendiente(dias_para_sorteo=15)

    send_payment_reminders()

    with Session(engine) as session:
        reservation = session.get(Reservation, reservation_id)
        assert reservation.reminder_sent_at is not None


def test_job_no_renotifica_si_ya_se_envio(monkeypatch):
    calls = []

    def fake_send(phone, template, params):
        calls.append(phone)
        return True

    monkeypatch.setattr("app.services.recordatorio.send_whatsapp", fake_send)
    _, _, reservation_id = _setup_raffle_con_reserva_pendiente(dias_para_sorteo=15)

    send_payment_reminders()
    primeras = len([c for c in calls if c == "+573002223344"])

    send_payment_reminders()
    segundas = len([c for c in calls if c == "+573002223344"])

    assert primeras == 1
    assert segundas == 1  # no se volvió a enviar


def test_job_no_notifica_rifas_fuera_de_ventana(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "app.services.recordatorio.send_whatsapp",
        lambda phone, *a, **kw: calls.append(phone) or True,
    )

    # Rifa que sortea en 30 días — fuera de la ventana de 14-16 días
    _setup_raffle_con_reserva_pendiente(dias_para_sorteo=30)

    send_payment_reminders()

    assert "+573002223344" not in calls


def test_job_no_notifica_reservas_pagadas(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "app.services.recordatorio.send_whatsapp",
        lambda phone, *a, **kw: calls.append(phone) or True,
    )

    token, raffle, reservation_id = _setup_raffle_con_reserva_pendiente(dias_para_sorteo=15)
    # confirmar pago → status=paid
    client.patch(
        f"/reservations/{reservation_id}/confirm-cash",
        headers={"Authorization": f"Bearer {token}"},
    )

    send_payment_reminders()

    assert "+573002223344" not in calls


def test_job_es_idempotente(monkeypatch):
    monkeypatch.setattr("app.services.recordatorio.send_whatsapp", lambda *a, **kw: True)
    _, _, reservation_id = _setup_raffle_con_reserva_pendiente(dias_para_sorteo=15)

    # correr 5 veces no debe generar estado inconsistente
    for _ in range(5):
        send_payment_reminders()

    with Session(engine) as session:
        reservation = session.get(Reservation, reservation_id)
        assert reservation.reminder_sent_at is not None
