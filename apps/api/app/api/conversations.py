from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.models import Conversation, Message, Contact
from app.schemas.schemas import ConversationResponse, MessageResponse

router = APIRouter()

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).order_by(Conversation.last_message_at.desc()))
    conversations = result.scalars().all()
    response = []
    for c in conversations:
        msgs = []
        for m in c.messages[-50:]:
            msgs.append(MessageResponse(id=str(m.id), external_message_id=m.external_message_id, direction=m.direction, content=m.content, message_type=m.message_type, timestamp=m.timestamp, created_at=m.created_at))
        response.append(ConversationResponse(id=str(c.id), contact_id=str(c.contact_id), is_locked=c.is_locked, last_message_at=c.last_message_at, created_at=c.created_at, updated_at=c.updated_at, messages=msgs))
    return response

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = []
    for m in conversation.messages[-100:]:
        msgs.append(MessageResponse(id=str(m.id), external_message_id=m.external_message_id, direction=m.direction, content=m.content, message_type=m.message_type, timestamp=m.timestamp, created_at=m.created_at))
    return ConversationResponse(id=str(conversation.id), contact_id=str(conversation.contact_id), is_locked=conversation.is_locked, last_message_at=conversation.last_message_at, created_at=conversation.created_at, updated_at=conversation.updated_at, messages=msgs)
