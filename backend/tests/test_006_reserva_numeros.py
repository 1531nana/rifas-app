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
    return create.json()


def test_reserva_exitosa_metodo_efectivo():
    raffle = _register_and_create_raffle()
    public_token = raffle["public_token"]

    response = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 10,
            "buyer_name": "Juan Perez",
            "buyer_phone": "+573001112233",
            "payment_method": "cash",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["number"] == 10
    assert data["status"] == "pending"
    # 5 dias para efectivo
    expires = datetime.fromisoformat(data["expires_at"])
    delta = expires - datetime.utcnow()
    assert delta.days >= 4


def test_reserva_exitosa_metodo_digital():
    raffle = _register_and_create_raffle()
    public_token = raffle["public_token"]

    response = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 15,
            "buyer_name": "Maria Lopez",
            "buyer_phone": "+573009998877",
            "payment_method": "card",
        },
    )
    assert response.status_code == 201
    data = response.json()
    # 48h para digital
    expires = datetime.fromisoformat(data["expires_at"])
    delta = expires - datetime.utcnow()
    assert delta.total_seconds() <= 48 * 3600 + 60


def test_reserva_numero_ya_tomado_retorna_409():
    raffle = _register_and_create_raffle()
    public_token = raffle["public_token"]

    client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 7,
            "buyer_name": "Primer Comprador",
            "buyer_phone": "+573001112233",
            "payment_method": "cash",
        },
    )

    response = client.post(
        f"/r/{public_token}/reserve",
        json={
            "number": 7,
            "buyer_name": "Segundo Comprador",
            "buyer_phone": "+573004445566",
            "payment_method": "cash",
        },
    )
    assert response.status_code == 409


def test_reserva_celular_invalido_retorna_422():
    raffle = _register_and_create_raffle()
    public_token = raffle["public_token"]

    for phone in ["123", "3001112233", "abc-def-ghij", "573001112233"]:
        response = client.post(
            f"/r/{public_token}/reserve",
            json={
                "number": 1,
                "buyer_name": "Comprador",
                "buyer_phone": phone,  # sin prefijo + internacional
                "payment_method": "cash",
            },
        )
        assert response.status_code == 422, f"Se esperaba 422 para celular '{phone}'"


def test_reserva_celular_formato_internacional_valido():
    raffle = _register_and_create_raffle()
    public_token = raffle["public_token"]

    for phone in ["+573001112233", "+1 800 555 1234", "+44 20 7946 0958"]:
        response = client.post(
            f"/r/{public_token}/reserve",
            json={
                "number": raffle["total_numbers"] - 1,
                "buyer_name": "Comprador",
                "buyer_phone": phone,
                "payment_method": "cash",
            },
        )
        # reset usando un numero diferente por cada llamada
        # solo verificamos que el formato no es rechazado por validacion (puede ser 409 si ya existe)
        assert response.status_code in (201, 409)
