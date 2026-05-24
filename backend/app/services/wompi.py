import hashlib
from urllib.parse import quote, urlencode

from app.models.domain import Reservation

WOMPI_CHECKOUT_BASE = "https://checkout.wompi.co/p/"
REFERENCIA_PREFIJO = "rifas-reserva"


def referencia_reserva(reservation_id: int) -> str:
    return f"{REFERENCIA_PREFIJO}-{reservation_id}"


def reservation_id_desde_referencia(referencia: str) -> int | None:
    try:
        return int(referencia.split("-")[-1])
    except (ValueError, IndexError):
        return None


def firma_integridad(reference: str, amount_in_cents: int, currency: str, integrity_key: str) -> str:
    """SHA256(reference + amount_in_cents + currency + integrity_key)"""
    raw = f"{reference}{amount_in_cents}{currency}{integrity_key}"
    return hashlib.sha256(raw.encode()).hexdigest()


def generar_url_checkout(
    reservation: Reservation,
    ticket_price: int,
    public_key: str,
    integrity_key: str,
    redirect_url: str,
) -> str:
    reference = referencia_reserva(reservation.id or 0)
    amount_in_cents = ticket_price * 100
    currency = "COP"

    firma = firma_integridad(reference, amount_in_cents, currency, integrity_key)
    # urlencode codifica ':' como '%3A' en las claves, pero Wompi requiere 'signature:integrity' literal.
    # Se construye la query manualmente para preservar el colon.
    params_base = {
        "public-key": public_key,
        "currency": currency,
        "amount-in-cents": str(amount_in_cents),
        "reference": reference,
        # "redirect-url": redirect_url, # TODO: No redirige correctamente debido a que estamos desde nuestro servidor local
    }
    query = urlencode(params_base) + f"&signature:integrity={quote(firma, safe='')}"
    return f"{WOMPI_CHECKOUT_BASE}?{query}"


def validar_firma_webhook(payload: dict, events_key: str) -> bool:
    """
    Valida la firma del webhook segun el algoritmo oficial de Wompi:
    SHA256(prop_values + timestamp + events_key)
    """
    try:
        signature = payload["signature"]
        properties: list[str] = signature["properties"]
        checksum: str = signature["checksum"]
        timestamp: int = payload["timestamp"]

        concatenated = ""
        data = payload["data"]
        for prop in properties:
            value: dict = data
            for key in prop.split("."):
                value = value[key]
            concatenated += str(value)
        concatenated += str(timestamp)
        concatenated += events_key

        computed = hashlib.sha256(concatenated.encode()).hexdigest()
        return computed == checksum
    except (KeyError, TypeError):
        return False


def extraer_referencia_y_estado(payload: dict) -> tuple[str, str] | None:
    """Extrae (referencia, estado) de un webhook transaction.updated. None si no aplica."""
    if payload.get("event") != "transaction.updated":
        return None
    transaction = payload.get("data", {}).get("transaction", {})
    referencia = transaction.get("reference", "")
    estado = transaction.get("status", "")
    if not referencia or not estado:
        return None
    return referencia, estado
