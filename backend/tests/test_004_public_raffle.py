from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.database import create_db_and_tables, engine
from app.main import app
from app.models.domain import Raffle, RaffleStatus

create_db_and_tables()
client = TestClient(app)


def _register_and_create_raffle(name="Rifa Test", total_numbers=50):
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
            "name": name,
            "lottery_type": "Loteria de Bogota",
            "total_numbers": total_numbers,
            "ticket_price": 10000,
            "prize_description": "Premio de prueba",
            "draw_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        },
    )
    assert create.status_code == 201
    return create.json()


def test_public_raffle_returns_404_for_unknown_token():
    response = client.get("/r/token-que-no-existe-xyz")
    assert response.status_code == 404


def test_public_raffle_returns_info_without_auth():
    raffle = _register_and_create_raffle("Rifa Publica")
    public_token = raffle["public_token"]

    response = client.get(f"/r/{public_token}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Rifa Publica"
    assert "prize_description" in data
    assert "draw_date" in data
    assert "ticket_price" in data
    assert "lottery_type" in data
    assert data["status"] == "active"


def test_public_raffle_closed_returns_closed_status():
    raffle = _register_and_create_raffle("Rifa Cerrada")
    public_token = raffle["public_token"]
    raffle_id = raffle["id"]

    with Session(engine) as session:
        db_raffle = session.exec(select(Raffle).where(Raffle.id == raffle_id)).first()
        db_raffle.status = RaffleStatus.closed
        session.add(db_raffle)
        session.commit()

    response = client.get(f"/r/{public_token}")
    assert response.status_code == 200
    assert response.json()["status"] == "closed"
