from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import create_db_and_tables
from app.main import app
from app.services.notifications import send_whatsapp
from app.services.raffles import MAX_IMAGE_BYTES, upload_to_cloudinary

create_db_and_tables()
client = TestClient(app)


def _register_and_create_raffle(total_numbers: int = 50) -> tuple[str, dict]:
    email = f"admin-{uuid4().hex}@example.com"
    register = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Admin Issues 10 11"},
    )
    assert register.status_code == 201
    token = register.json()["access_token"]

    create = client.post(
        "/raffles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Rifa Premio Imagen",
            "lottery_type": "Loteria de Bogota",
            "total_numbers": total_numbers,
            "ticket_price": 25000,
            "prize_description": "Moto nueva 125cc",
            "draw_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        },
    )
    assert create.status_code == 201
    return token, create.json()


def test_upload_prize_image_validates_and_exposes_public_url():
    token, raffle = _register_and_create_raffle()

    upload = client.post(
        f"/raffles/{raffle['id']}/image",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("premio.png", b"\x89PNG\r\n\x1a\nfake", "image/png")},
    )

    assert upload.status_code == 200
    image_url = upload.json()["prize_image_url"]
    assert image_url.endswith(".png")
    assert "/uploads/" in image_url

    public = client.get(f"/public/raffles/{raffle['public_token']}")
    assert public.status_code == 200
    assert public.json()["prize_image_url"] == image_url


def test_upload_prize_image_rejects_invalid_format_and_size():
    token, raffle = _register_and_create_raffle()

    invalid = client.post(
        f"/raffles/{raffle['id']}/image",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("premio.txt", b"texto", "text/plain")},
    )
    assert invalid.status_code == 400

    too_large = client.post(
        f"/raffles/{raffle['id']}/image",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("premio.jpg", b"x" * (MAX_IMAGE_BYTES + 1), "image/jpeg")},
    )
    assert too_large.status_code == 413


def test_upload_to_cloudinary_returns_secure_url(monkeypatch):
    captured = {}

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"secure_url": "https://res.cloudinary.com/demo/image/upload/premio.webp"}

    def fake_post(url, data, files, timeout):
        captured["url"] = url
        captured["data"] = data
        captured["files"] = files
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("app.services.raffles.httpx.post", fake_post)
    settings = SimpleNamespace(cloudinary_cloud_name="demo", cloudinary_upload_preset="preset")

    image_url = upload_to_cloudinary(settings, "premio.webp", b"img", "image/webp")

    assert image_url.startswith("https://res.cloudinary.com/")
    assert captured["url"] == "https://api.cloudinary.com/v1_1/demo/image/upload"
    assert captured["data"]["upload_preset"] == "preset"


def test_confirm_cash_payment_sends_whatsapp_from_short_endpoint(monkeypatch):
    calls = []
    token, raffle = _register_and_create_raffle()

    reservation = client.post(
        f"/r/{raffle['public_token']}/reserve",
        json={
            "number": 8,
            "buyer_name": "Comprador WhatsApp",
            "buyer_phone": "+573001112233",
            "payment_method": "cash",
        },
    )
    assert reservation.status_code == 201

    def fake_send(phone, template, params):
        calls.append({"phone": phone, "template": template, "params": params})
        return True

    monkeypatch.setattr("app.services.raffles.send_whatsapp", fake_send)
    confirmed = client.patch(
        f"/reservations/{reservation.json()['id']}/confirm-cash",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "paid"
    assert calls == [
        {
            "phone": "+573001112233",
            "template": "payment_confirmation",
            "params": {
                "buyer_name": "Comprador WhatsApp",
                "number": 8,
                "raffle_name": "Rifa Premio Imagen",
                "draw_date": raffle["draw_date"],
            },
        }
    ]


def test_send_whatsapp_uses_meta_cloud_api_and_handles_errors(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

    settings = SimpleNamespace(
        meta_sandbox=False,
        meta_api_token="token",
        meta_phone_number_id="123456",
        meta_graph_version="v20.0",
        meta_language_code="es_CO",
    )

    def fake_settings():
        return settings

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("app.services.notifications.get_settings", fake_settings)
    monkeypatch.setattr("app.services.notifications.httpx.post", fake_post)

    assert send_whatsapp("+573001112233", "payment_confirmation", {"name": "Ana", "number": 8}) is True
    assert captured["url"] == "https://graph.facebook.com/v20.0/123456/messages"
    assert captured["headers"]["Authorization"] == "Bearer token"
    assert captured["json"]["template"]["name"] == "payment_confirmation"

    def failing_post(*args, **kwargs):
        raise RuntimeError("meta down")

    monkeypatch.setattr("app.services.notifications.httpx.post", failing_post)
    assert send_whatsapp("+573001112233", "payment_confirmation", {"name": "Ana"}) is False
