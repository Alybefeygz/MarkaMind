from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class ConversationResponse(BaseModel):
    """API response schema for Conversation"""
    id: UUID
    chatbot_id: UUID
    session_id: str
    user_input: str
    bot_response: str
    source_entry_id: Optional[UUID] = None
    latency_ms: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ConversationList(BaseModel):
    """Schema for conversation list view"""
    id: UUID
    user_input: str  # Truncated for display
    bot_response: str  # Truncated for display  
    latency_ms: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ConversationStats(BaseModel):
    """Schema for conversation statistics"""
    total_conversations: int
    avg_latency: float
    rating_avg: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackResponse(BaseModel):
    """API response schema for Feedback"""
    id: UUID
    conversation_id: UUID
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ChatWidgetMessage(BaseModel):
    """Schema for chat widget messages"""
    message: str
    timestamp: datetime
    is_user: bool
    
    model_config = ConfigDict(from_attributes=True)