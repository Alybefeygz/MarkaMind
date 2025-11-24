from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any


class AIUsageLogCreate(BaseModel):
    """AI Usage Log oluşturma şeması"""
    usage_type: str = Field(..., description="chunk_enrichment, chat_response, summarization, embedding_generation, custom")
    chunk_id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    knowledge_entry_id: Optional[UUID] = None
    chatbot_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    model_name: str
    input_text: str
    output_text: Optional[str] = None
    input_tokens: Optional[int] = Field(None, ge=0)
    output_tokens: Optional[int] = Field(None, ge=0)
    total_tokens: Optional[int] = Field(None, ge=0)
    latency_ms: int = Field(..., ge=0)
    status: str = Field(default="success")
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AIUsageLogResponse(BaseModel):
    """AI Usage Log response şeması"""
    id: UUID
    usage_type: str
    chunk_id: Optional[UUID]
    conversation_id: Optional[UUID]
    knowledge_entry_id: Optional[UUID]
    chatbot_id: Optional[UUID]
    user_id: Optional[UUID]
    model_name: str
    input_text: str
    output_text: Optional[str]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    latency_ms: int
    status: str
    error_message: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class AIUsageLogStats(BaseModel):
    """AI kullanım istatistikleri"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_tokens: int
    total_cost: float  # Estimated cost
    avg_latency_ms: float
    by_usage_type: Dict[str, int]
    by_model: Dict[str, int]
