from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.models import Message, Approval, OutboundJob, SystemEvent, EventType
from datetime import datetime, timedelta
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/health/ready")
async def health_ready(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(select(1))
        return {"status": "ready", "database": "ok"}
    except Exception:
        return {"status": "not_ready", "database": "error"}

@router.get("/overview")
async def overview(db: AsyncSession = Depends(get_db)):
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    messages_today = await db.execute(select(func.count(Message.id)).where(Message.timestamp >= today_start))
    messages_today_count = messages_today.scalar() or 0
    pending_approvals = await db.execute(select(func.count(Approval.id)).where(Approval.status == "pending"))
    pending_approvals_count = pending_approvals.scalar() or 0
    failed_jobs = await db.execute(select(func.count(OutboundJob.id)).where(OutboundJob.status == "dead_letter"))
    failed_jobs_count = failed_jobs.scalar() or 0
    return {
        "messages_today": messages_today_count,
        "pending_approvals": pending_approvals_count,
        "failed_jobs": failed_jobs_count,
        "mode": settings.CONFIDENCE_THRESHOLD,
    }
