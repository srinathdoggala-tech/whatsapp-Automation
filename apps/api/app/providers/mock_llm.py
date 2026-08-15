from __future__ import annotations

import random
import time
from app.providers.llm import LLMProvider, GenerateResponseRequest, GenerateResponseResult

class MockLLMProvider(LLMProvider):
    async def generate_response(self, request: GenerateResponseRequest) -> GenerateResponseResult:
        await __import__("asyncio").sleep(random.uniform(0.05, 0.25))
        latest = request.incoming_messages[-1].get("content", "") if request.incoming_messages else ""
        replies = [
            f"Got it — {latest[:40]}{'...' if len(latest) > 40 else ''}",
            "Sounds good, I'll check and get back to you.",
            "Haha okay 😅",
            "On it.",
            "Let me look into that.",
        ]
        text = random.choice(replies)
        return GenerateResponseResult(
            response=text,
            confidence=0.85,
            intent="casual_conversation",
            needs_review=False,
            latency_ms=random.randint(40, 220),
            token_usage={"total_tokens": random.randint(20, 120)},
            raw={"provider": "mock"},
        )
