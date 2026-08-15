from __future__ import annotations

import google.generativeai as genai
from app.core.config import settings
from app.providers.llm import LLMProvider, GenerateResponseRequest, GenerateResponseResult
import time

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        api_key = api_key or settings.GEMINI_API_KEY
        model_name = model_name or settings.GEMINI_MODEL
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self._model = genai.GenerativeModel(model_name)

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
        response = await self._model.generate_content_async(prompt)
        text = getattr(response, "text", "") or ""
        latency_ms = int((time.perf_counter() - start) * 1000)
        usage = getattr(response, "usage_metadata", None)
        token_usage = None
        if usage:
            token_usage = {
                "prompt_tokens": getattr(usage, "prompt_token_count", None),
                "candidates_tokens": getattr(usage, "candidates_token_count", None),
                "total_tokens": getattr(usage, "total_token_count", None),
            }
        return GenerateResponseResult(
            response=text.strip(),
            confidence=0.9 if text else 0.0,
            needs_review=len(text.strip()) == 0,
            latency_ms=latency_ms,
            token_usage=token_usage,
            raw={"model": self.model_name},
        )
