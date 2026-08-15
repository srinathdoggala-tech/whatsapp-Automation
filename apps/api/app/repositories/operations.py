from __future__ import annotations

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import (
    AIInteraction,
    Approval,
    AuditLog,
    Conversation,
    Contact,
    Message,
    OutboundJob,
    SystemEvent,
    User,
    EventType,
    OutboundStatus,
)
from app.schemas.schemas import ApprovalResponse, OutboundJobResponse, AIInteractionResponse

class AIInteractionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, message_id: str, model: str, prompt: str, response: str, intent: Optional[str], confidence: float, needs_review: bool, latency_ms: Optional[int], token_usage: Optional[dict]) -> AIInteraction:
        interaction = AIInteraction(
            message_id=message_id,
            model=model,
            prompt=prompt,
            response=response,
            intent=intent,
            confidence=confidence,
            needs_review=needs_review,
            latency_ms=latency_ms,
            token_usage=token_usage,
        )
        self.db.add(interaction)
        await self.db.flush()
        return interaction

class ApprovalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_pending(self, conversation_id: str, outbound_job_id: str, suggested_response: str) -> Approval:
        approval = Approval(
            conversation_id=conversation_id,
            outbound_job_id=outbound_job_id,
            status="pending",
            suggested_response=suggested_response,
        )
        self.db.add(approval)
        await self.db.flush()
        return approval

    async def get_pending(self) -> list[Approval]:
        result = await self.db.execute(select(Approval).where(Approval.status == "pending"))
        return list(result.scalars().all())

class OutboundJobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, conversation_id: str, message_id: Optional[str], payload: dict) -> OutboundJob:
        job = OutboundJob(
            conversation_id=conversation_id,
            message_id=message_id,
            status=OutboundStatus.PENDING,
            payload=payload,
        )
        self.db.add(job)
        await self.db.flush()
        return job

    async def mark_sent(self, job_id: str) -> None:
        result = await self.db.execute(select(OutboundJob).where(OutboundJob.id == job_id))
        job = result.scalar_one_or_none()
        if job:
            job.status = OutboundStatus.SENT
            job.sent_at = datetime.utcnow()
            await self.db.flush()

    async def mark_failed(self, job_id: str, error: str) -> None:
        result = await self.db.execute(select(OutboundJob).where(OutboundJob.id == job_id))
        job = result.scalar_one_or_none()
        if job:
            job.retry_count += 1
            if job.retry_count >= job.max_retries:
                job.status = OutboundStatus.DEAD_LETTER
            else:
                job.status = OutboundStatus.FAILED
            job.error = error
            await self.db.flush()

class AuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record(self, event_type: EventType, entity_type: str, entity_id: Optional[str], metadata: Optional[dict] = None, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> AuditLog:
        log = AuditLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log)
        await self.db.flush()
        return log

class SystemEventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record(self, level: str, source: str, message: str, metadata: Optional[dict] = None) -> SystemEvent:
        event = SystemEvent(level=level, source=source, message=message, metadata_json=metadata)
        self.db.add(event)
        await self.db.flush()
        return event
