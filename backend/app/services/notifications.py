import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_whatsapp(phone: str, template: str, params: dict[str, object] | None = None) -> bool:
    """Send a WhatsApp template message through Meta Cloud API.

    In local/sandbox mode this records the intent and returns success so the
    payment flow is never blocked by missing external credentials.
    """
    settings = get_settings()
    if settings.meta_sandbox or not settings.meta_api_token or not settings.meta_phone_number_id:
        logger.info("[SANDBOX] WhatsApp to %s with template %s: %s", phone, template, params or {})
        return True

    try:
        components = []
        if params:
            components.append(
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(value)}
                        for value in params.values()
                    ],
                }
            )

        response = httpx.post(
            f"https://graph.facebook.com/{settings.meta_graph_version}/{settings.meta_phone_number_id}/messages",
            headers={"Authorization": f"Bearer {settings.meta_api_token}"},
            json={
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "template",
                "template": {
                    "name": template,
                    "language": {"code": settings.meta_language_code},
                    "components": components,
                },
            },
            timeout=10,
        )
        response.raise_for_status()
        return True
    except Exception as exc:
        logger.exception("Error enviando WhatsApp; el flujo continua: %s", exc)
        return False
