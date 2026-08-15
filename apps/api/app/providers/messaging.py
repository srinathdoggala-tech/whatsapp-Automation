from __future__ import annotations

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional

class SendMessageRequest(BaseModel):
    to_phone_number: str
    body: str
    message_type: str = "text"

class SendMessageResult(BaseModel):
    message_id: str
    status: str
    raw: dict | None = None

class MessagingProvider(ABC):
    @abstractmethod
    async def send_message(self, request: SendMessageRequest) -> SendMessageResult:
        ...
