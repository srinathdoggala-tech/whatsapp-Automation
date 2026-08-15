from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel

class GenerateResponseRequest(BaseModel):
    conversation_id: str
    incoming_messages: list[dict]
    style_profile: dict | None = None
    memory: list[str] | None = None

class GenerateResponseResult(BaseModel):
    response: str
    confidence: float
    intent: str | None = None
    needs_review: bool = False
    latency_ms: int | None = None
    token_usage: dict | None = None
    raw: dict | None = None

class LLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, request: GenerateResponseRequest) -> GenerateResponseResult:
        ...
