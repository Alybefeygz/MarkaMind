"""
Chunk Enrichment Schemas
Pydantic models for chunk enrichment API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class EnrichmentRequest(BaseModel):
    """Request to start chunk enrichment"""
    knowledge_entry_id: UUID = Field(..., description="ID of the knowledge base entry to enrich")
    prompt_template: Optional[str] = Field(None, description="Custom AI prompt template (optional)")
    ai_model: Optional[str] = Field(None, description="AI model to use (optional)")


class EnrichmentJobResponse(BaseModel):
    """Response when starting enrichment job"""
    job_id: UUID
    knowledge_entry_id: UUID
    status: str
    message: str
    total_chunks: int
    created_at: datetime


class JobProgress(BaseModel):
    """Job progress information"""
    total_chunks: int
    processed_chunks: int
    failed_chunks: int
    percentage: float


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: UUID
    knowledge_entry_id: UUID
    chatbot_id: UUID
    status: str
    progress: JobProgress
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    error_message: Optional[str] = None


class ChunkEnrichmentData(BaseModel):
    """Enriched data for a single chunk"""
    summary: str = Field(..., description="1-2 sentence summary of the chunk")
    tags: List[str] = Field(..., description="3-5 key tags/keywords")
    key_concepts: List[str] = Field(..., description="Important concepts in the chunk")
    complexity_level: str = Field(..., description="beginner, intermediate, or advanced")
    language: str = Field(..., description="Language code (tr, en, etc.)")


class EnrichedChunkResponse(BaseModel):
    """Response for enriched chunk"""
    chunk_id: UUID
    chunk_index: int
    content_preview: str
    enrichment: ChunkEnrichmentData
    enriched_at: datetime


class JobListResponse(BaseModel):
    """List of enrichment jobs"""
    jobs: List[JobStatusResponse]
    total: int
    page: int
    size: int
