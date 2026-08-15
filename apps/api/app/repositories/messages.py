from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Message, Conversation
from app.schemas.schemas import IncomingMessage

class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_external_id(self, external_message_id: str) -> Message | None:
        result = await self.db.execute(select(Message).where(Message.external_message_id == external_message_id))
        return result.scalar_one_or_none()

    async def create(self, conversation_id: str, incoming: IncomingMessage) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            external_message_id=incoming.message_id,
            direction="inbound",
            content=incoming.content,
            message_type=incoming.message_type,
            metadata_json={
                "phone_number": incoming.phone_number,
                "display_name": incoming.display_name,
                "timestamp": incoming.timestamp.isoformat() if incoming.timestamp else None,
            },
            timestamp=incoming.timestamp or datetime.utcnow(),
        )
        self.db.add(msg)
        await self.db.flush()
        return msg
