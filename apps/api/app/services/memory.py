from __future__ import annotations

from typing import List, Optional
from app.models.models import ConversationMemory
from app.schemas.schemas import ApprovalResponse

class MemoryService:
    def __init__(self, db):
        self.db = db

    async def add_memory(self, conversation_id: str, content: str, memory_type: str = "fact", relevance_score: float = 0.5) -> ConversationMemory:
        memory = ConversationMemory(
            conversation_id=conversation_id,
            memory_type=memory_type,
            content=content,
            relevance_score=relevance_score,
        )
        self.db.add(memory)
        await self.db.flush()
        return memory

    async def get_recent_memories(self, conversation_id: str, limit: int = 20) -> List[ConversationMemory]:
        from sqlalchemy import select
        result = await self.db.execute(
            select(ConversationMemory)
            .where(ConversationMemory.conversation_id == conversation_id)
            .order_by(ConversationMemory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
