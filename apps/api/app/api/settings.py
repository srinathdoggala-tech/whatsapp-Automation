from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.services.style import StyleService

router = APIRouter()

class AutomationControlRequest(BaseModel):
    mode: str

class SettingsUpdateRequest(BaseModel):
    min_delay: Optional[int] = None
    max_delay: Optional[int] = None
    burst_window_ms: Optional[int] = None
    confidence_threshold: Optional[float] = None
    max_auto_reply_length: Optional[int] = None

@router.get("/settings")
async def get_settings():
    return {
        "mode": "approval",
        "min_delay": settings.MIN_RESPONSE_DELAY,
        "max_delay": settings.MAX_RESPONSE_DELAY,
        "burst_window_ms": settings.BURST_WINDOW_MS,
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
        "max_auto_reply_length": settings.MAX_AUTO_REPLY_LENGTH,
    }

@router.post("/automation/pause")
async def pause_automation():
    return {"status": "paused"}

@router.post("/automation/resume")
async def resume_automation():
    return {"status": "resumed"}
