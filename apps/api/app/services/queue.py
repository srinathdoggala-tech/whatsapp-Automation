from __future__ import annotations

from redis.asyncio import Redis
from app.core.config import settings

class QueueService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.stream_key = "whatsapp:inbound"
        self.group = "workers"
        self.consumer = "worker-1"

    async def ensure_group(self) -> None:
        try:
            await self.redis.xgroup_create(self.stream_key, self.group, id="$", mkstream=True)
        except Exception:
            pass

    async def enqueue(self, payload: dict) -> None:
        await self.redis.xadd(self.stream_key, payload)

    async def read_batch(self, count: int = 10, block_ms: int = 5000):
        try:
            results = await self.redis.xreadgroup(
                groupname=self.group,
                consumername=self.consumer,
                streams={self.stream_key: ">"},
                count=count,
                block=block_ms,
            )
            return results
        except Exception:
            return []

    async def ack(self, message_id: str) -> None:
        await self.redis.xack(self.stream_key, self.group, message_id)
