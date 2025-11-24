from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List


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


# ============================================
# CHUNK SCHEMAS
# ============================================

class ChunkResponse(BaseModel):
    """Schema for knowledge chunk"""
    id: UUID
    knowledge_entry_id: UUID
    chatbot_id: UUID
    chunk_index: int
    content: str
    token_count: int
    metadata: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChunkListItem(BaseModel):
    """Schema for chunk list view (without full content)"""
    id: UUID
    chunk_index: int
    content_preview: str  # First 100 characters
    token_count: int
    metadata: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class ProcessChunksRequest(BaseModel):
    """Request schema for processing chunks"""
    chunk_size: int = Field(default=1000, ge=100, le=5000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    force_reprocess: bool = Field(default=False)


class ProcessChunksResponse(BaseModel):
    """Response schema for chunk processing"""
    success: bool
    source_id: UUID
    chunks_created: int
    total_tokens: int
    average_chunk_size: int
    processing_time_ms: int
    chunks_preview: Optional[List[ChunkListItem]] = None

    model_config = ConfigDict(from_attributes=True)


class ChunkStatistics(BaseModel):
    """Statistics for chunks"""
    total_chunks: int
    total_tokens: int
    average_chunk_size: int
    min_chunk_size: int
    max_chunk_size: int