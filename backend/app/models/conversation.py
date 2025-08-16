from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class ConversationBase(BaseModel):
    """Base Conversation model with common fields"""
    session_id: str = Field(..., min_length=1, max_length=100)
    user_input: str = Field(..., min_length=1, max_length=2000)
    bot_response: str = Field(..., min_length=1, max_length=5000)
    latency_ms: int = 0


class ConversationCreate(ConversationBase):
    """Conversation model for creation requests"""
    chatbot_id: UUID
    source_entry_id: Optional[UUID] = None


class Conversation(ConversationBase):
    """Complete Conversation model with all fields"""
    id: UUID
    chatbot_id: UUID
    source_entry_id: Optional[UUID] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackBase(BaseModel):
    """Base Feedback model with common fields"""
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)


class FeedbackCreate(FeedbackBase):
    """Feedback model for creation requests"""
    conversation_id: UUID


class Feedback(FeedbackBase):
    """Complete Feedback model with all fields"""
    id: UUID
    conversation_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)