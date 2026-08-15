from __future__ import annotations

import httpx
from app.core.config import settings
from app.providers.llm import LLMProvider, GenerateResponseRequest, GenerateResponseResult
import time

class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None, api_url: str | None = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL
        self.api_url = api_url or settings.OPENROUTER_API_URL
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")

    async def generate_response(self, request: GenerateResponseRequest) -> GenerateResponseResult:
        start = time.perf_counter()
        history_text = ""
        for m in request.incoming_messages:
            history_text += f"User: {m.get('content', '')}\n"
        prompt = (
            "You are the user's personal WhatsApp assistant. Reply naturally in the user's style.\n"
            "Keep it concise. Do not invent facts. Ask for approval if uncertain.\n\n"
            f"Style guidance: {(request.style_profile or {}).get('tone', 'casual')}\n\n"
            f"Context:\n{history_text}\nAssistant:"
        )
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://example.com",
            "X-Title": "WhatsApp AI Assistant",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
            "temperature": 0.7,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(self.api_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        latency_ms = int((time.perf_counter() - start) * 1000)
        usage = data.get("usage", {})
        return GenerateResponseResult(
            response=text or "",
            confidence=0.9 if text else 0.0,
            needs_review=len(text) == 0,
            latency_ms=latency_ms,
            token_usage={"total_tokens": usage.get("total_tokens")},
            raw={"provider": "openrouter", "model": self.model},
        )
