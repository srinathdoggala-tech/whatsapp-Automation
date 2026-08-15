from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AutomationMode(str, Enum):
    AUTOPILOT = "autopilot"
    APPROVAL = "approval"
    PAUSED = "paused"

class OutboundStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"
    CANCELLED = "cancelled"

class ContactBase(BaseModel):
    phone_number: str
    display_name: Optional[str] = None
    automation_mode: AutomationMode = AutomationMode.APPROVAL
    min_delay_seconds: Optional[int] = None
    max_delay_seconds: Optional[int] = None
    is_ignored: bool = False

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    message_type: str = "text"

class MessageResponse(MessageBase):
    id: str
    external_message_id: str
    direction: str
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    contact_id: str
    is_locked: bool
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True

class ApprovalResponse(BaseModel):
    id: str
    conversation_id: str
    status: str
    suggested_response: str
    edited_response: Optional[str]
    reason: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class OutboundJobResponse(BaseModel):
    id: str
    conversation_id: str
    status: OutboundStatus
    retry_count: int
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    error: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AIInteractionResponse(BaseModel):
    id: str
    model: str
    response: str
    latency_ms: Optional[int]
    intent: Optional[str]
    confidence: Optional[float]
    needs_review: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class SystemSettingsResponse(BaseModel):
    mode: AutomationMode
    min_delay: int
    max_delay: int
    burst_window_ms: int
    confidence_threshold: float
    max_auto_reply_length: int

class StyleProfileResponse(BaseModel):
    id: str
    profile_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WebhookPayload(BaseModel):
    object: str
    entry: List[Dict[str, Any]]

class IncomingMessage(BaseModel):
    message_id: str
    phone_number: str
    display_name: Optional[str]
    content: str
    timestamp: Optional[datetime]
    message_type: str = "text"
