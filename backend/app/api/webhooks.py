from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.config import Settings, get_settings
from app.core.database import get_session
from app.models.schemas_pagos import WompiWebhookPayload
from app.services import pagos, wompi

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/wompi", status_code=200)
def webhook_wompi(
    payload: WompiWebhookPayload,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> dict:
    if not wompi.validar_firma_webhook(payload.model_dump(), settings.wompi_events_key):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Firma invalida")

    resultado = wompi.extraer_referencia_y_estado(payload.model_dump())
    if resultado is None:
        return {"ok": True}

    referencia, estado = resultado
    reservation_id = wompi.reservation_id_desde_referencia(referencia)
    if reservation_id is None:
        return {"ok": True}

    if estado == "APPROVED":
        pagos.confirmar_pago(session, reservation_id)
    elif estado in ("DECLINED", "VOIDED", "ERROR"):
        pagos.cancelar_pago(session, reservation_id)

    return {"ok": True}
