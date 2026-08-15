from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.core.database import engine
from app.core.config import settings
from app.core.redis import redis as redis_client
from app.services.queue import QueueService
from app.services.idempotency import IdempotencyService
from app.services.timing import ResponseTimingEngine
from app.services.validation import ValidationService
from app.services.memory import MemoryService
from app.services.style import StyleService
from app.repositories.contacts import ContactRepository, ConversationRepository
from app.repositories.messages import MessageRepository
from app.repositories.operations import (
    AIInteractionRepository,
    ApprovalRepository,
    OutboundJobRepository,
    AuditLogRepository,
    SystemEventRepository,
)
from app.providers.llm import GenerateResponseRequest, GenerateResponseResult
from app.providers.mock_llm import MockLLMProvider
from app.providers.mock_messaging import MockMessagingProvider
from app.models.models import EventType

logger = logging.getLogger("worker")
logging.basicConfig(level=logging.INFO)

session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def process_burst(session: AsyncSession, conversation_id: str, messages: list[dict], contact_phone: str) -> None:
    timing = ResponseTimingEngine()
    validation = ValidationService(confidence_threshold=settings.CONFIDENCE_THRESHOLD, max_length=settings.MAX_AUTO_REPLY_LENGTH)
    memory_service = MemoryService(session)
    style_service = StyleService(session)
    ai_repo = AIInteractionRepository(session)
    approval_repo = ApprovalRepository(session)
    outbound_repo = OutboundJobRepository(session)
    audit_repo = AuditLogRepository(session)
    event_repo = SystemEventRepository(session)
    messaging = MockMessagingProvider()
    llm = MockLLMProvider()
    style_profile = await style_service.get_profile(user_id="default")
    context = messages[-5:]
    request = GenerateResponseRequest(conversation_id=conversation_id, incoming_messages=context, style_profile=style_profile)
    try:
        result: GenerateResponseResult = await llm.generate_response(request)
    except Exception as exc:
        await event_repo.record("error", "worker", f"LLM generation failed: {exc}")
        return
    await ai_repo.create(
        message_id=messages[-1].get("message_id"),
        model=getattr(result, "raw", {}).get("model", "mock"),
        prompt="",
        response=result.response,
        intent=result.intent,
        confidence=result.confidence,
        needs_review=result.needs_review,
        latency_ms=result.latency_ms,
        token_usage=result.token_usage,
    )
    needs_approval, reason = validation.to_approval_if_needed(confidence=result.confidence, needs_review=result.needs_review, response=result.response)
    if needs_approval:
        job = await outbound_repo.create(conversation_id=conversation_id, message_id=messages[-1].get("message_id"), payload={"response": result.response, "reason": reason})
        await approval_repo.create_pending(conversation_id=conversation_id, outbound_job_id=str(job.id), suggested_response=result.response)
        await audit_repo.record(EventType.APPROVAL_CREATED, "approval", str(job.id), metadata={"reason": reason})
        return
    delay = timing.calculate_delay(incoming_count=len(messages))
    await asyncio.sleep(delay)
    send_result = await messaging.send_message(request=type("Obj", (), {"to_phone_number": contact_phone, "body": result.response, "message_type": "text"})())
    job = await outbound_repo.create(conversation_id=conversation_id, message_id=messages[-1].get("message_id"), payload={"response": result.response})
    await outbound_repo.mark_sent(str(job.id))
    await audit_repo.record(EventType.RESPONSE_SENT, "outbound_job", str(job.id), metadata={"status": send_result.status})

async def run_worker() -> None:
    queue = QueueService(redis_client)
    await queue.ensure_group()
    logger.info("Worker started")
    while True:
        try:
            batches = await queue.read_batch(count=10, block_ms=5000)
            if not batches:
                continue
            for stream, messages in batches:
                for message_id, data in messages:
                    await queue.ack(message_id)
                    conversation_id = data.get("conversation_id")
                    external_message_id = data.get("external_message_id")
                    async with session_factory() as session:
                        idemp = IdempotencyService()
                        if await idemp.is_processed(external_message_id):
                            continue
                        await idemp.mark_processed(external_message_id)
                        messages_list = [{"message_id": external_message_id, "content": data.get("content", "")}]
                        await process_burst(session, conversation_id, messages_list, data.get("phone_number", ""))
                    await asyncio.sleep(0)
        except Exception:
            logger.exception("Worker error")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_worker())
