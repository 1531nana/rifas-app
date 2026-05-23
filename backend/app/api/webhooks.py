from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.models.schemas import WebhookResult, WompiWebhookPayload
from app.services.raffles import process_wompi_webhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/wompi", response_model=WebhookResult)
def wompi_webhook(payload: WompiWebhookPayload, session: Session = Depends(get_session)) -> WebhookResult:
    return process_wompi_webhook(session, payload.model_dump(exclude_none=True))
