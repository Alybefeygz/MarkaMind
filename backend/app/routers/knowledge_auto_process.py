"""
Knowledge Auto-Process Router
PDF yüklendikten sonra otomatik chunking ve enrichment başlatır
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from uuid import UUID
import logging

from ..dependencies import get_current_user, get_supabase_client
from ..services.chunking_service import ChunkingService
from ..services.chunk_enrichment_service import chunk_enrichment_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge Auto-Process"],
    responses={404: {"description": "Not found"}}
)


async def auto_process_pdf_chunks_and_enrich(
    knowledge_entry_id: str,
    chatbot_id: str,
    user_id: str,
    supabase
):
    """
    Background task: PDF'i otomatik chunklara ayırır ve enrichment başlatır

    Args:
        knowledge_entry_id: Knowledge base entry ID
        chatbot_id: Chatbot ID
        user_id: User ID
        supabase: Supabase client
    """
    try:
        logger.info(f"🚀 Auto-processing started for knowledge entry {knowledge_entry_id}")

        # 1. Knowledge entry'yi al
        source_result = supabase.table("knowledge_base_entries").select(
            "id, source_name, content, status"
        ).eq("id", knowledge_entry_id).execute()

        if not source_result.data:
            logger.error(f"Knowledge entry not found: {knowledge_entry_id}")
            return

        source = source_result.data[0]

        # 2. Content var mı kontrol et
        if not source.get("content"):
            logger.warning(f"No content in knowledge entry {knowledge_entry_id}")
            # Status'u failed yap
            supabase.table("knowledge_base_entries").update({
                "status": "failed",
                "error_message": "No content to process"
            }).eq("id", knowledge_entry_id).execute()
            return

        # 3. Chunk'lara ayır
        logger.info(f"📝 Chunking text for {knowledge_entry_id}")

        chunker = ChunkingService(
            chunk_size=1000,
            chunk_overlap=200,
            min_chunk_size=100
        )

        chunks = chunker.chunk_text(
            text=source["content"],
            source_name=source.get("source_name", "")
        )

        if not chunks:
            logger.error(f"Failed to create chunks for {knowledge_entry_id}")
            supabase.table("knowledge_base_entries").update({
                "status": "failed",
                "error_message": "Failed to create chunks"
            }).eq("id", knowledge_entry_id).execute()
            return

        # 4. Chunk'ları veritabanına kaydet
        logger.info(f"💾 Saving {len(chunks)} chunks to database")

        chunk_records = []
        for chunk in chunks:
            chunk_records.append({
                "knowledge_entry_id": knowledge_entry_id,
                "chatbot_id": chatbot_id,
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
                "token_count": chunk["token_count"],
                "metadata": chunk["metadata"]
            })

        insert_result = supabase.table("knowledge_chunks").insert(chunk_records).execute()

        if not insert_result.data:
            logger.error(f"Failed to insert chunks for {knowledge_entry_id}")
            supabase.table("knowledge_base_entries").update({
                "status": "failed",
                "error_message": "Failed to save chunks"
            }).eq("id", knowledge_entry_id).execute()
            return

        # 5. Status'u processed yap
        supabase.table("knowledge_base_entries").update({
            "status": "processed"
        }).eq("id", knowledge_entry_id).execute()

        logger.info(f"✅ Chunking completed: {len(chunks)} chunks created")

        # 6. Enrichment job oluştur ve başlat
        logger.info(f"🤖 Starting AI enrichment for {knowledge_entry_id}")

        try:
            job = await chunk_enrichment_service.create_enrichment_job(
                knowledge_entry_id=knowledge_entry_id,
                chatbot_id=chatbot_id,
                user_id=user_id,
                prompt_template=None,
                ai_model=None  # Default Gemini kullan
            )

            # Background'da enrichment başlat
            await chunk_enrichment_service.enrich_all_chunks_background(
                job_id=job['id'],
                knowledge_entry_id=knowledge_entry_id,
                prompt_template=None,
                ai_model=None,
                chatbot_id=chatbot_id,
                user_id=user_id
            )

            logger.info(f"✅ AI enrichment completed for {knowledge_entry_id}")

        except Exception as e:
            logger.error(f"⚠️ Enrichment failed for {knowledge_entry_id}: {e}")
            # Enrichment hatası ana akışı bozmamalı

    except Exception as e:
        logger.error(f"❌ Auto-process failed for {knowledge_entry_id}: {e}")
        try:
            supabase.table("knowledge_base_entries").update({
                "status": "failed",
                "error_message": str(e)[:500]
            }).eq("id", knowledge_entry_id).execute()
        except:
            pass


@router.post("/trigger-auto-process/{knowledge_entry_id}")
async def trigger_auto_process(
    knowledge_entry_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    PDF upload edildikten sonra bu endpoint'i çağırın.
    Otomatik chunking ve AI enrichment başlatır.

    **Kullanım:**
    1. PDF'i Supabase storage'a yükle
    2. knowledge_base_entries tablosuna kayıt oluştur
    3. Bu endpoint'i çağır (background'da chunk+enrich başlar)

    **Background'da yapılanlar:**
    - ✅ PDF text → chunks
    - ✅ Chunks → AI enrichment (özet, tag, key concepts)
    - ✅ AI usage logging
    """
    try:
        # 1. Knowledge entry'yi kontrol et ve ownership doğrula
        knowledge_result = supabase.table("knowledge_base_entries").select(
            "id, chatbot_id, status, chatbots!inner(brands!inner(user_id))"
        ).eq("id", str(knowledge_entry_id)).eq(
            "chatbots.brands.user_id", current_user["id"]
        ).execute()

        if not knowledge_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge entry not found or you don't have permission"
            )

        knowledge_entry = knowledge_result.data[0]
        chatbot_id = knowledge_entry['chatbot_id']

        # 2. Status'u processing yap
        supabase.table("knowledge_base_entries").update({
            "status": "processing"
        }).eq("id", str(knowledge_entry_id)).execute()

        # 3. Background task başlat
        background_tasks.add_task(
            auto_process_pdf_chunks_and_enrich,
            knowledge_entry_id=str(knowledge_entry_id),
            chatbot_id=chatbot_id,
            user_id=current_user["id"],
            supabase=supabase
        )

        logger.info(f"✅ Auto-process triggered for {knowledge_entry_id}")

        return {
            "success": True,
            "message": "Auto-processing started (chunking + AI enrichment)",
            "knowledge_entry_id": str(knowledge_entry_id),
            "status": "processing"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger auto-process: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger auto-process: {str(e)}"
        )
