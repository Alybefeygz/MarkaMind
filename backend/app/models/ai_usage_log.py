from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any


class AIUsageLogBase(BaseModel):
    """Base AI Usage Log model"""
    usage_type: str = Field(..., description="AI kullanım tipi: chunk_enrichment, chat_response, vs.")
    chunk_id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    knowledge_entry_id: Optional[UUID] = None
    chatbot_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    model_name: str = Field(..., description="Kullanılan AI model adı")
    input_text: str = Field(..., description="AI'ya gönderilen input")
    output_text: Optional[str] = None
    input_tokens: Optional[int] = Field(None, ge=0)
    output_tokens: Optional[int] = Field(None, ge=0)
    total_tokens: Optional[int] = Field(None, ge=0)
    latency_ms: int = Field(..., ge=0, description="İstek süresi (milisaniye)")
    status: str = Field(default="success", description="İstek durumu")
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AIUsageLogCreate(AIUsageLogBase):
    """AI Usage Log creation model"""
    pass


class AIUsageLog(AIUsageLogBase):
    """Complete AI Usage Log model"""
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
