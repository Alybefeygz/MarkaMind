"""
Chat Message Schemas
API request/response schemas for chat messages
"""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List, Literal


# ============================================
# REQUEST SCHEMAS
# ============================================

class SendMessageRequest(BaseModel):
    """Kullanıcı mesajı gönderme request'i"""
    chatbot_id: UUID
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: str = Field(..., min_length=1)

    # Opsiyonel - anonim kullanıcılar için
    user_id: Optional[UUID] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UpdateFeedbackRequest(BaseModel):
    """Mesaj geri bildirimi güncelleme"""
    was_helpful: Optional[bool] = None
    sentiment: Optional[Literal["positive", "negative", "neutral"]] = None
    user_feedback: Optional[str] = Field(None, max_length=1000)
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)


# ============================================
# RESPONSE SCHEMAS
# ============================================

class ChatMessageResponse(BaseModel):
    """Tek mesaj response"""
    id: UUID
    chatbot_id: UUID
    conversation_id: Optional[UUID]
    session_id: str

    user_id: Optional[UUID]

    message_direction: str
    message_type: str
    content: str
    formatted_content: Optional[Dict[str, Any]]

    ai_model: Optional[str]
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    processing_time_ms: Optional[int]

    status: str
    error_message: Optional[str]

    source_chunks: List[str]
    source_entry_id: Optional[UUID]

    sentiment: Optional[str]
    was_helpful: Optional[bool]
    user_feedback: Optional[str]
    feedback_rating: Optional[int]

    parent_message_id: Optional[UUID]
    thread_id: Optional[UUID]

    metadata: Dict[str, Any]

    created_at: datetime
    updated_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True


class SendMessageResponse(BaseModel):
    """Mesaj gönderme sonucu"""
    success: bool
    user_message_id: UUID
    bot_message_id: UUID
    bot_response: str
    processing_time_ms: int
    total_tokens: Optional[int]
    session_id: str

    # Kullanılan kaynaklar
    source_chunks: List[str] = Field(default_factory=list)
    source_entry_id: Optional[UUID] = None


class ConversationHistoryResponse(BaseModel):
    """Konuşma geçmişi response"""
    session_id: str
    chatbot_id: UUID
    messages: List[ChatMessageResponse]
    total_messages: int

    # Conversation istatistikleri
    stats: Dict[str, Any] = Field(default_factory=dict)
    # Örnek: {
    #   "total_user_messages": 10,
    #   "total_bot_messages": 10,
    #   "avg_response_time_ms": 1234,
    #   "satisfaction_rate": 0.85
    # }


class ChatSessionResponse(BaseModel):
    """Chat session bilgisi"""
    session_id: str
    chatbot_id: UUID
    chatbot_name: str

    user_id: Optional[UUID]

    first_message_at: datetime
    last_message_at: datetime
    total_messages: int

    avg_response_time_ms: Optional[float]
    satisfaction_rate: Optional[float]


class ChatSessionListResponse(BaseModel):
    """Chat session listesi"""
    sessions: List[ChatSessionResponse]
    total: int
    page: int
    size: int
    pages: int


class ChatStatisticsResponse(BaseModel):
    """Chat istatistikleri"""
    chatbot_id: UUID
    period: str  # "today", "week", "month", "all"

    total_messages: int
    total_user_messages: int
    total_bot_messages: int
    total_sessions: int
    unique_users: int

    avg_response_time_ms: float
    p95_response_time_ms: float

    satisfaction_rate: Optional[float]
    positive_feedback_count: int
    negative_feedback_count: int

    avg_tokens_per_message: Optional[float]
    total_tokens_used: Optional[int]

    top_error_types: List[Dict[str, Any]] = Field(default_factory=list)
    # Örnek: [{"error_code": "timeout", "count": 5}, ...]

    messages_by_hour: List[Dict[str, Any]] = Field(default_factory=list)
    # Örnek: [{"hour": 14, "count": 123}, ...]
