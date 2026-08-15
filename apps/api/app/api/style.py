from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.services.style import StyleService

router = APIRouter()

class StyleUpdateRequest(BaseModel):
    profile_data: dict

@router.get("/style")
async def get_style(db: AsyncSession = Depends(get_db)):
    service = StyleService(db)
    data = await service.get_profile(user_id="default")
    return {"profile_data": data}

@router.put("/style")
async def update_style(request: StyleUpdateRequest, db: AsyncSession = Depends(get_db)):
    service = StyleService(db)
    profile = await service.save_profile(user_id="default", profile_data=request.profile_data)
    return {"profile_data": profile.profile_data}
