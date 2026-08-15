from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.idempotency import IdempotencyService
from app.repositories.contacts import ContactRepository, ConversationRepository
from app.repositories.messages import MessageRepository
from app.schemas.schemas import IncomingMessage, WebhookPayload
from app.services.queue import QueueService
from app.core.redis import redis as redis_client
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
idempotency = IdempotencyService()

@router.get("/webhooks/whatsapp")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(challenge) if challenge else {"status": "ok"}
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhooks/whatsapp")
async def webhook(payload: WebhookPayload, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        entry = payload.entry[0] if payload.entry else {}
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return {"status": "ignored"}
        message = messages[0]
        phone_number = message.get("from", "")
        display_name = value.get("contacts", [{}])[0].get("profile", {}).get("name")
        content = ""
        if message.get("type") == "text":
            content = message.get("text", {}).get("body", "")
        incoming = IncomingMessage(
            message_id=message.get("id", ""),
            phone_number=phone_number,
            display_name=display_name,
            content=content,
            timestamp=datetime.fromtimestamp(int(message.get("timestamp", 0))) if message.get("timestamp") else None,
            message_type=message.get("type", "text"),
        )
        if await idempotency.is_processed(incoming.message_id):
            return {"status": "duplicate"}
        contact_repo = ContactRepository(db)
        conversation_repo = ConversationRepository(db)
        message_repo = MessageRepository(db)
        contact = await contact_repo.get_or_create_by_phone(user_id="default", phone_number=incoming.phone_number, display_name=incoming.display_name)
        conversation = await conversation_repo.get_or_create_by_contact(contact_id=str(contact.id))
        msg = await message_repo.create(conversation_id=str(conversation.id), incoming=incoming)
        await idempotency.mark_processed(incoming.message_id)
        queue = QueueService(redis_client)
        await queue.enqueue({
            "type": "inbound_message",
            "message_id": str(msg.id),
            "conversation_id": str(conversation.id),
            "external_message_id": incoming.message_id,
            "phone_number": incoming.phone_number,
            "content": incoming.content,
        })
        return {"status": "queued"}
    except Exception:
        logger.exception("Webhook processing failed")
        return {"status": "error"}
