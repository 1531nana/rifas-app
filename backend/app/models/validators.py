import re

# Formato internacional E.164 / WhatsApp: + seguido de codigo de pais y numero
PHONE_RE = re.compile(r"^\+\d[\d\s\-]{6,29}$")


def validate_phone(value: str) -> str:
    if not PHONE_RE.match(value):
        raise ValueError("El celular debe estar en formato internacional (ej: +573001112233)")
    return value
