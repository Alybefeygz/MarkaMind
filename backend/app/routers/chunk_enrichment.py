"""
Chunk Enrichment Router
API endpoints for AI chunk enrichment
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List
from uuid import UUID
import logging

from app.schemas.chunk_enrichment import (
    EnrichmentRequest,
    EnrichmentJobResponse,
    JobStatusResponse,
    JobListResponse
)
from app.dependencies import get_current_user, get_supabase_client
from app.services.chunk_enrichment_service import chunk_enrichment_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chunks",
    tags=["Chunk Enrichment"],
    responses={404: {"description": "Not found"}}
)


@router.post("/enrich", response_model=EnrichmentJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_chunk_enrichment(
    request: EnrichmentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    📝 PDF chunk'larını AI ile zenginleştirme işlemini başlatır (Arka planda çalışır)

    Bu endpoint:
    - Chunk'lar için özet oluşturur
    - Tag'ler çıkarır
    - Ana kavramları belirler
    - Karmaşıklık seviyesini analiz eder

    İşlem arka planda asenkron olarak çalışır.
    Durumu kontrol etmek için GET /chunks/enrich/{job_id}/status endpoint'ini kullanın.
    """
    try:
        # 1. Knowledge entry'yi kontrol et ve ownership doğrula
        knowledge_result = supabase.table("knowledge_base_entries").select(
            "id, chatbot_id, source_name, chatbots!inner(brands!inner(user_id))"
        ).eq("id", str(request.knowledge_entry_id)).eq(
            "chatbots.brands.user_id", current_user["id"]
        ).execute()

        if not knowledge_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge entry not found or you don't have permission"
            )

        knowledge_entry = knowledge_result.data[0]
        chatbot_id = knowledge_entry['chatbot_id']

        # 2. Chunk'ların var olduğunu kontrol et
        chunks_result = supabase.table("knowledge_chunks").select(
            "id", count="exact"
        ).eq("knowledge_entry_id", str(request.knowledge_entry_id)).execute()

        if not chunks_result.count or chunks_result.count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No chunks found. Please process the PDF into chunks first."
            )

        # 3. Enrichment job oluştur
        job = await chunk_enrichment_service.create_enrichment_job(
            knowledge_entry_id=str(request.knowledge_entry_id),
            chatbot_id=chatbot_id,
            user_id=current_user["id"],
            prompt_template=request.prompt_template,
            ai_model=request.ai_model
        )

        # 4. Arka plan görevi başlat (AI loglama için chatbot_id ve user_id eklendi)
        background_tasks.add_task(
            chunk_enrichment_service.enrich_all_chunks_background,
            job_id=job['id'],
            knowledge_entry_id=str(request.knowledge_entry_id),
            prompt_template=request.prompt_template,
            ai_model=request.ai_model,
            chatbot_id=chatbot_id,
            user_id=current_user["id"]
        )

        logger.info(f"Started enrichment job {job['id']} for user {current_user['id']}")

        return EnrichmentJobResponse(
            job_id=job['id'],
            knowledge_entry_id=request.knowledge_entry_id,
            status=job['status'],
            message=f"Enrichment job started for {chunks_result.count} chunks",
            total_chunks=chunks_result.count,
            created_at=job['created_at']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start enrichment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start enrichment: {str(e)}"
        )


@router.get("/enrich/{job_id}/status", response_model=JobStatusResponse)
async def get_enrichment_job_status(
    job_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    📊 Chunk enrichment işleminin durumunu kontrol eder

    Returns:
        - İşlem durumu (pending, processing, completed, failed)
        - İlerleme yüzdesi
        - İşlenen chunk sayısı
        - Başlangıç ve bitiş zamanları
    """
    try:
        # Job'u al ve ownership kontrol et
        job_result = supabase.table("chunk_enrichment_jobs").select(
            "*"
        ).eq("id", str(job_id)).eq("user_id", current_user["id"]).execute()

        if not job_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrichment job not found or you don't have permission"
            )

        # Status bilgisi al
        job_status = await chunk_enrichment_service.get_job_status(str(job_id))

        if not job_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job status not found"
            )

        return JobStatusResponse(
            job_id=job_status['id'],
            knowledge_entry_id=job_status['knowledge_entry_id'],
            chatbot_id=job_status['chatbot_id'],
            status=job_status['status'],
            progress=job_status['progress'],
            started_at=job_status.get('started_at'),
            completed_at=job_status.get('completed_at'),
            created_at=job_status['created_at'],
            error_message=job_status.get('error_message')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/enrich/jobs", response_model=JobListResponse)
async def list_enrichment_jobs(
    page: int = 1,
    size: int = 20,
    status_filter: str = None,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    📋 Kullanıcının tüm enrichment job'larını listeler

    Query Parameters:
        - page: Sayfa numarası (varsayılan: 1)
        - size: Sayfa başına kayıt (varsayılan: 20)
        - status_filter: Durum filtresi (pending, processing, completed, failed)
    """
    try:
        # Offset hesapla
        offset = (page - 1) * size

        # Query oluştur
        query = supabase.table("chunk_enrichment_jobs").select(
            "*", count="exact"
        ).eq("user_id", current_user["id"])

        # Status filtresi
        if status_filter:
            query = query.eq("status", status_filter)

        # Sıralama ve pagination
        query = query.order("created_at", desc=True).range(offset, offset + size - 1)

        result = query.execute()

        jobs = []
        for job_data in result.data:
            # Progress hesapla
            percentage = 0
            if job_data['total_chunks'] > 0:
                percentage = (job_data['processed_chunks'] / job_data['total_chunks']) * 100

            jobs.append(JobStatusResponse(
                job_id=job_data['id'],
                knowledge_entry_id=job_data['knowledge_entry_id'],
                chatbot_id=job_data['chatbot_id'],
                status=job_data['status'],
                progress={
                    "total_chunks": job_data['total_chunks'],
                    "processed_chunks": job_data['processed_chunks'],
                    "failed_chunks": job_data['failed_chunks'],
                    "percentage": round(percentage, 2)
                },
                started_at=job_data.get('started_at'),
                completed_at=job_data.get('completed_at'),
                created_at=job_data['created_at'],
                error_message=job_data.get('error_message')
            ))

        return JobListResponse(
            jobs=jobs,
            total=result.count or 0,
            page=page,
            size=size
        )

    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}"
        )


@router.delete("/enrich/{job_id}")
async def delete_enrichment_job(
    job_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    🗑️ Enrichment job'ı siler

    Not: Sadece tamamlanmış veya başarısız job'lar silinebilir.
    İşlem devam eden job'lar silinemez.
    """
    try:
        # Job'u kontrol et
        job_result = supabase.table("chunk_enrichment_jobs").select(
            "id, status"
        ).eq("id", str(job_id)).eq("user_id", current_user["id"]).execute()

        if not job_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        job = job_result.data[0]

        # Processing durumundaki job'lar silinemez
        if job['status'] == 'processing':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete a job that is currently processing"
            )

        # Sil
        supabase.table("chunk_enrichment_jobs").delete().eq("id", str(job_id)).execute()

        logger.info(f"Deleted enrichment job {job_id}")

        return {"success": True, "message": "Job deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}"
        )
