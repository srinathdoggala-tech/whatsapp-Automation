from __future__ import annotations

import json
from typing import Optional
from app.core.redis import redis as redis_client

class IdempotencyService:
    @staticmethod
    def key_for_message(external_message_id: str) -> str:
        return f"idempotency:message:{external_message_id}"

    @staticmethod
    def key_for_conversation(conversation_id: str) -> str:
        return f"lock:conversation:{conversation_id}"

    async def is_processed(self, external_message_id: str) -> bool:
        key = self.key_for_message(external_message_id)
        value = await redis_client.get(key)
        return value is not None

    async def mark_processed(self, external_message_id: str, ttl: int = 86400) -> None:
        key = self.key_for_message(external_message_id)
        await redis_client.set(key, "1", ex=ttl)

    async def acquire_lock(self, conversation_id: str, ttl: int = 60) -> bool:
        key = self.key_for_conversation(conversation_id)
        acquired = await redis_client.set(key, "1", nx=True, ex=ttl)
        return bool(acquired)

    async def release_lock(self, conversation_id: str) -> None:
        key = self.key_for_conversation(conversation_id)
        await redis_client.delete(key)
