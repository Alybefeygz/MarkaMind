from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
from uuid import UUID
import logging

from ..schemas.knowledge import KnowledgeResponse, KnowledgeUpdate, KnowledgeList, KnowledgeStats
from ..schemas.common import StatusResponse, PaginationParams, PaginationResponse
from ..models.knowledge import KnowledgeBaseEntryCreate
from ..dependencies import get_current_user, get_supabase_client
from .knowledge_auto_process import auto_process_pdf_chunks_and_enrich

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge Base"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_entry(
    knowledge: KnowledgeBaseEntryCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Create a new knowledge base entry for a chatbot

    **Otomatik İşleme:**
    - PDF yüklendikten sonra otomatik olarak chunking ve AI enrichment başlar
    - İşlem arka planda asenkron çalışır
    - Tüm AI istekleri ai_usage_logs tablosuna kaydedilir
    """
    try:
        # Verify chatbot belongs to user (through brand ownership)
        chatbot_result = supabase.table("chatbots").select(
            "id, brands!inner(user_id)"
        ).eq("id", str(knowledge.chatbot_id)).eq("brands.user_id", current_user["id"]).execute()

        if not chatbot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or not owned by user"
            )

        # Prepare knowledge data
        knowledge_data = knowledge.model_dump()

        # 🔒 GÜVENLİK: Frontend'den gelen status'u IGNORE et, her zaman 'pending' ile başla
        # Bu sayede otomatik işleme garantili olarak tetiklenir
        knowledge_data['status'] = 'pending'

        # Create knowledge entry in database
        result = supabase.table("knowledge_base_entries").insert(knowledge_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create knowledge entry"
            )

        created_entry = result.data[0]
        knowledge_entry_id = created_entry['id']

        # 🚀 OTOMATIK İŞLEME: Chunking + AI Enrichment başlat
        # Eğer content varsa (PDF text extract edilmişse), otomatik işleme başlat
        if created_entry.get('content'):
            logger.info(f"🚀 Auto-triggering chunking + AI enrichment for knowledge entry {knowledge_entry_id}")

            # Status'u processing yap
            supabase.table("knowledge_base_entries").update({
                "status": "processing"
            }).eq("id", knowledge_entry_id).execute()

            # Background task başlat
            background_tasks.add_task(
                auto_process_pdf_chunks_and_enrich,
                knowledge_entry_id=knowledge_entry_id,
                chatbot_id=str(knowledge.chatbot_id),
                user_id=current_user["id"],
                supabase=supabase
            )

            # Response'da status'u processing olarak göster
            created_entry['status'] = 'processing'

            logger.info(f"✅ Auto-processing queued for {knowledge_entry_id}")
        else:
            logger.warning(f"⚠️ No content in knowledge entry {knowledge_entry_id}, skipping auto-processing")

        return KnowledgeResponse(**created_entry)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create knowledge entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create knowledge entry: {str(e)}"
        )


@router.get("/", response_model=PaginationResponse[KnowledgeList])
async def list_knowledge_entries(
    pagination: PaginationParams = Depends(),
    chatbot_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get list of knowledge base entries with pagination
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size
        
        # Build query - join with chatbots and brands to ensure user ownership
        query = supabase.table("knowledge_base_entries").select(
            "id, source_type, source_url, status, token_count, created_at, chatbots!inner(brands!inner(user_id))",
            count="exact"
        ).eq("chatbots.brands.user_id", current_user["id"])
        
        # Apply filters
        if chatbot_id:
            query = query.eq("chatbot_id", str(chatbot_id))
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        # Get total count
        count_result = query.execute()
        total = count_result.count if count_result.count else 0
        
        # Get knowledge entries with pagination
        query = query.order(pagination.sort or "created_at", desc=True).range(offset, offset + pagination.size - 1)
        result = query.execute()
        
        # Process results to exclude nested fields from response
        knowledge_entries = []
        if result.data:
            for item in result.data:
                # Remove the nested fields before creating KnowledgeList
                knowledge_data = {k: v for k, v in item.items() if k != "chatbots"}
                knowledge_entries.append(KnowledgeList(**knowledge_data))
        
        return PaginationResponse(
            items=knowledge_entries,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge entries: {str(e)}"
        )


@router.get("/{knowledge_id}", response_model=KnowledgeResponse)
async def get_knowledge_entry(
    knowledge_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get a specific knowledge base entry by ID
    """
    try:
        # Get knowledge entry with ownership check
        result = supabase.table("knowledge_base_entries").select(
            "*, chatbots!inner(brands!inner(user_id))"
        ).eq("id", str(knowledge_id)).eq("chatbots.brands.user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge entry not found"
            )
        
        # Remove nested fields from response
        knowledge_data = {k: v for k, v in result.data[0].items() if k != "chatbots"}
        return KnowledgeResponse(**knowledge_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge entry: {str(e)}"
        )


@router.put("/{knowledge_id}", response_model=KnowledgeResponse)
async def update_knowledge_entry(
    knowledge_id: UUID,
    knowledge_update: KnowledgeUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update a specific knowledge base entry
    """
    try:
        # Check if knowledge entry exists and user owns it
        existing = supabase.table("knowledge_base_entries").select(
            "id, chatbots!inner(brands!inner(user_id))"
        ).eq("id", str(knowledge_id)).eq("chatbots.brands.user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge entry not found"
            )
        
        # Prepare update data
        update_data = knowledge_update.model_dump(exclude_unset=True)
        
        # Update knowledge entry
        result = supabase.table("knowledge_base_entries").update(update_data).eq("id", str(knowledge_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update knowledge entry"
            )
        
        return KnowledgeResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update knowledge entry: {str(e)}"
        )


@router.delete("/{knowledge_id}", response_model=StatusResponse)
async def delete_knowledge_entry(
    knowledge_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete a specific knowledge base entry
    """
    try:
        # Check if knowledge entry exists and user owns it
        existing = supabase.table("knowledge_base_entries").select(
            "id, chatbots!inner(brands!inner(user_id))"
        ).eq("id", str(knowledge_id)).eq("chatbots.brands.user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge entry not found"
            )
        
        # Delete knowledge entry
        result = supabase.table("knowledge_base_entries").delete().eq("id", str(knowledge_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete knowledge entry"
            )
        
        return StatusResponse(
            success=True,
            message="Knowledge entry deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete knowledge entry: {str(e)}"
        )


@router.get("/chatbot/{chatbot_id}/stats", response_model=KnowledgeStats)
async def get_chatbot_knowledge_stats(
    chatbot_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get knowledge base statistics for a specific chatbot
    """
    try:
        # Verify chatbot belongs to user
        chatbot_result = supabase.table("chatbots").select(
            "id, brands!inner(user_id)"
        ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
        
        if not chatbot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or not owned by user"
            )
        
        # Get knowledge entries for this chatbot
        result = supabase.table("knowledge_base_entries").select(
            "status, token_count"
        ).eq("chatbot_id", str(chatbot_id)).execute()
        
        if not result.data:
            return KnowledgeStats(
                total_entries=0,
                total_tokens=0,
                status_counts={}
            )
        
        # Calculate statistics
        total_entries = len(result.data)
        total_tokens = sum(entry.get("token_count", 0) for entry in result.data)
        
        # Count entries by status
        status_counts = {}
        for entry in result.data:
            status = entry.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return KnowledgeStats(
            total_entries=total_entries,
            total_tokens=total_tokens,
            status_counts=status_counts
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge stats: {str(e)}"
        )


@router.patch("/{knowledge_id}/process", response_model=StatusResponse)
async def process_knowledge_entry(
    knowledge_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Mark a knowledge entry as processed (placeholder for actual processing logic)
    """
    try:
        # Check if knowledge entry exists and user owns it
        existing = supabase.table("knowledge_base_entries").select(
            "id, status, chatbots!inner(brands!inner(user_id))"
        ).eq("id", str(knowledge_id)).eq("chatbots.brands.user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge entry not found"
            )
        
        current_status = existing.data[0].get("status")
        
        if current_status == "processed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Knowledge entry is already processed"
            )
        
        # Update status to processed
        result = supabase.table("knowledge_base_entries").update({
            "status": "processed"
        }).eq("id", str(knowledge_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process knowledge entry"
            )
        
        return StatusResponse(
            success=True,
            message="Knowledge entry marked as processed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process knowledge entry: {str(e)}"
        )


@router.post("/batch-delete", response_model=StatusResponse)
async def batch_delete_knowledge_entries(
    knowledge_ids: List[UUID],
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete multiple knowledge base entries at once
    """
    try:
        if not knowledge_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No knowledge entry IDs provided"
            )
        
        # Convert UUIDs to strings
        id_strings = [str(kid) for kid in knowledge_ids]
        
        # Verify all entries belong to the user
        existing = supabase.table("knowledge_base_entries").select(
            "id, chatbots!inner(brands!inner(user_id))"
        ).in_("id", id_strings).eq("chatbots.brands.user_id", current_user["id"]).execute()
        
        if not existing.data or len(existing.data) != len(knowledge_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more knowledge entries not found or not owned by user"
            )
        
        # Delete all entries
        result = supabase.table("knowledge_base_entries").delete().in_("id", id_strings).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete knowledge entries"
            )
        
        return StatusResponse(
            success=True,
            message=f"Successfully deleted {len(result.data)} knowledge entries"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch delete knowledge entries: {str(e)}"
        )