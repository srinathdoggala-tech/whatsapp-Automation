from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, ForeignKey, Enum as SQLEnum, Index, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base

class AutomationMode(str, enum.Enum):
    AUTOPILOT = "autopilot"
    APPROVAL = "approval"
    PAUSED = "paused"

class OutboundStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"
    CANCELLED = "cancelled"

class EventType(str, enum.Enum):
    WEBHOOK_RECEIVED = "webhook_received"
    WEBHOOK_DUPLICATE = "webhook_duplicate"
    MESSAGE_PROCESSED = "message_processed"
    RESPONSE_GENERATED = "response_generated"
    RESPONSE_SENT = "response_sent"
    RESPONSE_FAILED = "response_failed"
    APPROVAL_CREATED = "approval_created"
    APPROVAL_SENT = "approval_sent"
    APPROVAL_REJECTED = "approval_rejected"
    SYSTEM_ERROR = "system_error"
    LOCK_ACQUIRED = "lock_acquired"
    LOCK_RELEASED = "lock_released"
    LOCK_TIMEOUT = "lock_timeout"

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contacts = relationship("Contact", back_populates="user")

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    automation_mode = Column(SQLEnum(AutomationMode), default=AutomationMode.APPROVAL)
    min_delay_seconds = Column(Integer, nullable=True)
    max_delay_seconds = Column(Integer, nullable=True)
    is_ignored = Column(Boolean, default=False)
    style_override = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="contacts")
    conversations = relationship("Conversation", back_populates="contact")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contact_id = Column(String(36), ForeignKey("contacts.id"), nullable=False)
    is_locked = Column(Boolean, default=False)
    lock_acquired_at = Column(DateTime, nullable=True)
    lock_expires_at = Column(DateTime, nullable=True)
    last_message_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contact = relationship("Contact", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.timestamp")
    memories = relationship("ConversationMemory", back_populates="conversation")
    approvals = relationship("Approval", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    external_message_id = Column(String(255), unique=True, nullable=False, index=True)
    direction = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_timestamp", "conversation_id", "timestamp"),
    )

class ConversationMemory(Base):
    __tablename__ = "conversation_memories"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    memory_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)
    relevance_score = Column(Float, nullable=True)
    source_message_id = Column(String(36), ForeignKey("messages.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("Conversation", back_populates="memories")

class StyleProfile(Base):
    __tablename__ = "style_profiles"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    profile_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AutomationSettings(Base):
    __tablename__ = "automation_settings"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIInteraction(Base):
    __tablename__ = "ai_interactions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey("messages.id"), nullable=False)
    model = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=True)
    response = Column(Text, nullable=False)
    latency_ms = Column(Integer, nullable=True)
    token_usage = Column(JSON, nullable=True)
    intent = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    needs_review = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class OutboundJob(Base):
    __tablename__ = "outbound_jobs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    message_id = Column(String(36), ForeignKey("messages.id"), nullable=True)
    status = Column(SQLEnum(OutboundStatus), default=OutboundStatus.PENDING, index=True)
    payload = Column(JSON, nullable=False)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Approval(Base):
    __tablename__ = "approvals"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    outbound_job_id = Column(String(36), ForeignKey("outbound_jobs.id"), nullable=True)
    status = Column(String(20), default="pending", index=True)
    suggested_response = Column(Text, nullable=False)
    edited_response = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    reviewed_by = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("Conversation", back_populates="approvals")
    outbound_job = relationship("OutboundJob")

class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(255), unique=True, nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)
    processed = Column(Boolean, default=False)
    error = Column(Text, nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class SystemEvent(Base):
    __tablename__ = "system_events"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    level = Column(String(20), nullable=False, index=True)
    source = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
