from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Contact, Conversation, AutomationMode

class ContactRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_by_phone(self, user_id: str, phone_number: str, display_name: Optional[str] = None) -> Contact:
        result = await self.db.execute(select(Contact).where(Contact.phone_number == phone_number))
        contact = result.scalar_one_or_none()
        if contact:
            if display_name and not contact.display_name:
                contact.display_name = display_name
            return contact
        contact = Contact(
            user_id=user_id,
            phone_number=phone_number,
            display_name=display_name,
        )
        self.db.add(contact)
        await self.db.flush()
        return contact

    async def get_by_phone(self, phone_number: str) -> Contact | None:
        result = await self.db.execute(select(Contact).where(Contact.phone_number == phone_number))
        return result.scalar_one_or_none()

class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_contact_id(self, contact_id: str) -> Conversation | None:
        result = await self.db.execute(select(Conversation).where(Conversation.contact_id == contact_id))
        return result.scalar_one_or_none()

    async def get_or_create_by_contact(self, contact_id: str) -> Conversation:
        conversation = await self.get_by_contact_id(contact_id)
        if conversation:
            return conversation
        conversation = Conversation(contact_id=contact_id)
        self.db.add(conversation)
        await self.db.flush()
        return conversation
