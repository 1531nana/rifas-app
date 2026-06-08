from pydantic import BaseModel

class CheckoutResponse(BaseModel):
    checkout_url: str
    referencia: str


class WompiWebhookPayload(BaseModel):
    event: str
    data: dict
    environment: str | None = None
    timestamp: int
    sent_at: str | None = None
    signature: dict
