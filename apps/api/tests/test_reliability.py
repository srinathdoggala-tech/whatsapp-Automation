from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base
from app.core.config import Settings
from app.core.database import get_db
from app.main import app
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["SECRET_KEY"] = "test"
os.environ["GEMINI_API_KEY"] = "test"
os.environ["WHATSAPP_VERIFY_TOKEN"] = "test"


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

    async def xadd(self, stream, message):
        return "ok"

    async def xgroup_create(self, stream, group, id="$", mkstream=False):
        return "OK"

    async def xreadgroup(self, groupname, consumername, streams, count=10, block=0):
        return []

    async def xack(self, stream, group, message_id):
        return True


@pytest.fixture
def fake_redis(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr("app.core.redis.redis", fake)
    monkeypatch.setattr("app.services.idempotency.redis_client", fake)
    monkeypatch.setattr("app.api.webhook.redis_client", fake)
    return fake


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session, fake_redis):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_webhook_duplicate_is_ignored(client: AsyncClient, fake_redis: FakeRedis):
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "msg_duplicate_1",
                                    "from": "1234567890",
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {"body": "hello"},
                                }
                            ],
                            "contacts": [{"profile": {"name": "Test"}}],
                        }
                    }
                ]
            }
        ],
    }
    r1 = await client.post("/api/webhooks/whatsapp", json=payload)
    r2 = await client.post("/api/webhooks/whatsapp", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["status"] == "queued"
    assert r2.json()["status"] == "duplicate"


@pytest.mark.asyncio
async def test_overview(client: AsyncClient):
    resp = await client.get("/api/overview")
    assert resp.status_code == 200
    assert "messages_today" in resp.json()
