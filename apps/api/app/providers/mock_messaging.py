from __future__ import annotations

import uuid
import random
from app.providers.messaging import MessagingProvider, SendMessageRequest, SendMessageResult

class MockMessagingProvider(MessagingProvider):
    async def send_message(self, request: SendMessageRequest) -> SendMessageResult:
        await __import__("asyncio").sleep(random.uniform(0.02, 0.12))
        return SendMessageResult(
            message_id=f"mock_{uuid.uuid4().hex}",
            status="sent",
            raw={"provider": "mock", "to": request.to_phone_number},
        )
