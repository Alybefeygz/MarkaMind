"""
Chat Message Model
Chatbot mesajlaşma kayıtları için veri modeli
"""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List, Literal


class ChatMessageBase(BaseModel):
    """Base ChatMessage model with common fields"""
    chatbot_id: UUID
    conversation_id: Optional[UUID] = None
    session_id: str = Field(..., min_length=1)

    # Kullanıcı Bilgileri
    user_id: Optional[UUID] = None  # NULL = anonim kullanıcı
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

    # Mesaj İçeriği
    message_direction: Literal["incoming", "outgoing"] = Field(
        ...,
        description="incoming = kullanıcıdan gelen, outgoing = bot'tan giden"
    )
    message_type: Literal["text", "image", "file", "system", "error", "quick_reply"] = Field(
        default="text",
        description="Mesaj tipi"
    )
    content: str = Field(..., min_length=1)
    formatted_content: Optional[Dict[str, Any]] = None

    # AI İşleme Bilgileri
    ai_model: Optional[str] = None
    prompt_tokens: Optional[int] = Field(None, ge=0)
    completion_tokens: Optional[int] = Field(None, ge=0)
    total_tokens: Optional[int] = Field(None, ge=0)
    processing_time_ms: Optional[int] = Field(None, ge=0)

    # Response Bilgileri
    status: Literal["success", "failed", "timeout", "rate_limited", "pending"] = Field(
        default="success"
    )
    error_message: Optional[str] = None
    error_code: Optional[str] = None

    # Kaynak Bilgileri
    source_chunks: List[str] = Field(default_factory=list, description="Kullanılan chunk ID'leri")
    source_entry_id: Optional[UUID] = None

    # Kullanıcı Geri Bildirimi
    sentiment: Optional[Literal["positive", "negative", "neutral"]] = None
    was_helpful: Optional[bool] = None
    user_feedback: Optional[str] = None
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)

    # Thread/Reply Desteği
    parent_message_id: Optional[UUID] = None
    thread_id: Optional[UUID] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Zaman Damgaları
    read_at: Optional[datetime] = None


class ChatMessageCreate(ChatMessageBase):
    """ChatMessage model for creation requests"""
    pass


class ChatMessageUpdate(BaseModel):
    """ChatMessage model for update requests"""
    sentiment: Optional[Literal["positive", "negative", "neutral"]] = None
    was_helpful: Optional[bool] = None
    user_feedback: Optional[str] = None
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    read_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatMessage(ChatMessageBase):
    """Complete ChatMessage model with all fields"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
