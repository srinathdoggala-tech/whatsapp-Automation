from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.models import Approval
from app.schemas.schemas import ApprovalResponse

router = APIRouter()

@router.get("/approvals", response_model=List[ApprovalResponse])
async def list_approvals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Approval).where(Approval.status == "pending").order_by(Approval.created_at.asc()))
    approvals = result.scalars().all()
    return [
        ApprovalResponse(
            id=str(a.id),
            conversation_id=str(a.conversation_id),
            status=a.status,
            suggested_response=a.suggested_response,
            edited_response=a.edited_response,
            reason=a.reason,
            reviewed_by=a.reviewed_by,
            reviewed_at=a.reviewed_at,
            created_at=a.created_at,
        )
        for a in approvals
    ]

@router.post("/approvals/{approval_id}/send", response_model=ApprovalResponse)
async def send_approval(approval_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Approval).where(Approval.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval.status = "approved"
    approval.reviewed_at = datetime.utcnow()
    await db.flush()
    return ApprovalResponse(id=str(approval.id), conversation_id=str(approval.conversation_id), status=approval.status, suggested_response=approval.suggested_response, edited_response=approval.edited_response, reason=approval.reason, reviewed_by=approval.reviewed_by, reviewed_at=approval.reviewed_at, created_at=approval.created_at)

@router.post("/approvals/{approval_id}/reject", response_model=ApprovalResponse)
async def reject_approval(approval_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Approval).where(Approval.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval.status = "rejected"
    approval.reviewed_at = datetime.utcnow()
    await db.flush()
    return ApprovalResponse(id=str(approval.id), conversation_id=str(approval.conversation_id), status=approval.status, suggested_response=approval.suggested_response, edited_response=approval.edited_response, reason=approval.reason, reviewed_by=approval.reviewed_by, reviewed_at=approval.reviewed_at, created_at=approval.created_at)
