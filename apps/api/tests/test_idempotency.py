from __future__ import annotations

import pytest
from app.services.idempotency import IdempotencyService
from app.core.redis import redis as redis_client

pytestmark = pytest.mark.asyncio

class FakeRedis:
    def __init__(self):
        self.store: dict[str, str] = {}

    async def get(self, key):
        return self.store.get(key)

    async def set(self, key, value, ex=None, nx=False, xx=False):
        if nx and key in self.store:
            return False
        self.store[key] = value
        return True

    async def delete(self, key):
        self.store.pop(key, None)

@pytest.fixture
def service(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr("app.services.idempotency.redis_client", fake)
    return IdempotencyService()

async def test_duplicate_rejected(service):
    assert await service.is_processed("msg_1") is False
    await service.mark_processed("msg_1")
    assert await service.is_processed("msg_1") is True

async def test_lock(service):
    assert await service.acquire_lock("conv_1") is True
    assert await service.acquire_lock("conv_1") is False
    await service.release_lock("conv_1")
    assert await service.acquire_lock("conv_1") is True
