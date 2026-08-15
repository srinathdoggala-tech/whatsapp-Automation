from __future__ import annotations

from app.providers.messaging import MessagingProvider, SendMessageRequest, SendMessageResult
from app.core.config import settings

class WhatsAppCloudProvider(MessagingProvider):
    def __init__(self, access_token: str | None = None, phone_number_id: str | None = None):
        self.access_token = access_token or settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
        if not self.access_token or not self.phone_number_id:
            raise ValueError("WhatsApp credentials are required")

    async def send_message(self, request: SendMessageRequest) -> SendMessageResult:
        import httpx
        url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": request.to_phone_number,
            "type": request.message_type,
            request.message_type: {"body": {"text": request.body}},
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            message_id = data.get("messages", [{}])[0].get("id", "")
            return SendMessageResult(message_id=message_id, status="sent", raw=data)
