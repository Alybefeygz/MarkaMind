from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any


class KnowledgeResponse(BaseModel):
    """API response schema for KnowledgeBaseEntry"""
    id: UUID
    chatbot_id: UUID
    source_type: str
    source_url: Optional[HttpUrl] = None
    content: Optional[str] = None
    embedding_id: Optional[str] = None
    token_count: int
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgeUpdate(BaseModel):
    """Schema for updating knowledge base entry"""
    content: Optional[str] = Field(None, max_length=10000)
    status: Optional[str] = Field(None, pattern=r'^(pending|processing|processed|failed)$')


class KnowledgeList(BaseModel):
    """Schema for knowledge base entry list view"""
    id: UUID
    source_type: str
    source_url: Optional[str] = None  # Truncated URL for display
    status: str
    token_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgeStats(BaseModel):
    """Schema for knowledge base statistics"""
    total_entries: int
    total_tokens: int
    status_counts: Dict[str, int]
    
    model_config = ConfigDict(from_attributes=True)