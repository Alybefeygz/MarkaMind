from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from datetime import datetime
from uuid import UUID
from typing import Optional


class KnowledgeBaseEntryBase(BaseModel):
    """Base KnowledgeBaseEntry model with common fields"""
    source_type: str = Field(..., pattern=r'^(url|text|file|document)$')
    source_url: Optional[HttpUrl] = None
    content: Optional[str] = Field(None, max_length=10000)
    embedding_id: Optional[str] = None
    token_count: int = 0
    status: str = "pending"


class KnowledgeBaseEntryCreate(KnowledgeBaseEntryBase):
    """KnowledgeBaseEntry model for creation requests"""
    chatbot_id: UUID


class KnowledgeBaseEntry(KnowledgeBaseEntryBase):
    """Complete KnowledgeBaseEntry model with all fields"""
    id: UUID
    chatbot_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)