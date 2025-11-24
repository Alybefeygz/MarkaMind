"""
Chat Router
Chatbot mesajlaşma endpoint'leri
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional
from uuid import UUID
import logging

from app.schemas.chat_message import (
    SendMessageRequest,
    SendMessageResponse,
    UpdateFeedbackRequest,
    ChatMessageResponse,
    ConversationHistoryResponse
)
from app.schemas.common import StatusResponse
from app.dependencies import get_supabase_client
from app.services.chat_service import chat_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}}
)


@router.post("/send", response_model=SendMessageResponse, status_code=status.HTTP_200_OK)
async def send_message(
    request: SendMessageRequest,
    http_request: Request,
    supabase = Depends(get_supabase_client)
):
    """
    Kullanıcı mesajı gönder ve AI yanıtı al

    **Akış:**
    1. Kullanıcı mesajını kaydet (incoming)
    2. AI yanıtı üret (knowledge base + conversation history)
    3. Bot yanıtını kaydet (outgoing)
    4. AI usage log
    5. Response dön

    **Anonim Kullanıcı:**
    - `user_id` = None
    - `client_ip` otomatik tespit edilir
    - `session_id` frontend tarafından sağlanır

    **Kayıtlı Kullanıcı:**
    - `user_id` gönderilir
    - Mesajlar kullanıcı hesabıyla ilişkilendirilir
    """
    try:
        # Client IP'yi request'ten al
        client_ip = request.client_ip or http_request.client.host
        user_agent = http_request.headers.get("user-agent")

        # Mesajı gönder ve yanıtı al
        result = await chat_service.send_message(
            chatbot_id=str(request.chatbot_id),
            user_message=request.message,
            session_id=request.session_id,
            user_id=str(request.user_id) if request.user_id else None,
            client_ip=client_ip,
            user_agent=user_agent,
            metadata=request.metadata
        )

        return SendMessageResponse(**result)

    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str,
    chatbot_id: UUID,
    limit: int = 50,
    supabase = Depends(get_supabase_client)
):
    """
    Belirli bir session'ın mesaj geçmişini getir

    **Kullanım:**
    - Frontend chat widget açıldığında geçmiş mesajları yüklemek için
    - Kullanıcı sayfayı yenilediğinde conversation'ı restore etmek için

    **Query Parameters:**
    - `chatbot_id`: Chatbot ID (zorunlu)
    - `limit`: Maksimum mesaj sayısı (varsayılan: 50)
    """
    try:
        messages = await chat_service.get_conversation_history(
            session_id=session_id,
            chatbot_id=str(chatbot_id),
            limit=limit
        )

        # İstatistikler hesapla
        total_messages = len(messages)
        user_messages = [m for m in messages if m["message_direction"] == "incoming"]
        bot_messages = [m for m in messages if m["message_direction"] == "outgoing"]

        avg_response_time = 0
        if bot_messages:
            response_times = [m.get("processing_time_ms", 0) for m in bot_messages if m.get("processing_time_ms")]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)

        helpful_messages = [m for m in bot_messages if m.get("was_helpful") is not None]
        satisfaction_rate = 0
        if helpful_messages:
            helpful_count = len([m for m in helpful_messages if m["was_helpful"]])
            satisfaction_rate = helpful_count / len(helpful_messages)

        stats = {
            "total_user_messages": len(user_messages),
            "total_bot_messages": len(bot_messages),
            "avg_response_time_ms": avg_response_time,
            "satisfaction_rate": satisfaction_rate
        }

        return ConversationHistoryResponse(
            session_id=session_id,
            chatbot_id=chatbot_id,
            messages=messages,
            total_messages=total_messages,
            stats=stats
        )

    except Exception as e:
        logger.error(f"Failed to get conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )


@router.patch("/feedback/{message_id}", response_model=StatusResponse)
async def update_message_feedback(
    message_id: UUID,
    feedback: UpdateFeedbackRequest,
    supabase = Depends(get_supabase_client)
):
    """
    Mesaj geri bildirimini güncelle

    **Kullanım:**
    - Kullanıcı "👍 Yardımcı oldu" veya "👎 Yardımcı olmadı" butonuna tıkladığında
    - Kullanıcı yorum/puan verdiğinde

    **Body:**
    ```json
    {
      "was_helpful": true,
      "sentiment": "positive",
      "user_feedback": "Çok yardımcı oldu, teşekkürler!",
      "feedback_rating": 5
    }
    ```
    """
    try:
        success = await chat_service.update_feedback(
            message_id=str(message_id),
            was_helpful=feedback.was_helpful,
            sentiment=feedback.sentiment,
            user_feedback=feedback.user_feedback,
            feedback_rating=feedback.feedback_rating
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update feedback"
            )

        return StatusResponse(
            success=True,
            message="Feedback updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update feedback: {str(e)}"
        )


@router.get("/message/{message_id}", response_model=ChatMessageResponse)
async def get_message(
    message_id: UUID,
    supabase = Depends(get_supabase_client)
):
    """
    Tek bir mesajın detaylarını getir

    **Kullanım:**
    - Mesaj detaylarını görüntüleme
    - AI usage bilgilerini inceleme
    """
    try:
        result = supabase.table("chat_messages").select("*").eq("id", str(message_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )

        return ChatMessageResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get message: {str(e)}"
        )


@router.delete("/session/{session_id}", response_model=StatusResponse)
async def delete_session(
    session_id: str,
    chatbot_id: UUID,
    supabase = Depends(get_supabase_client)
):
    """
    Belirli bir session'ın tüm mesajlarını sil

    **UYARI:** Bu işlem geri alınamaz!

    **Kullanım:**
    - Kullanıcı conversation'ı temizlemek istediğinde
    - GDPR compliance (kullanıcı verilerini silme)
    """
    try:
        result = supabase.table("chat_messages").delete().eq(
            "session_id", session_id
        ).eq("chatbot_id", str(chatbot_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or already deleted"
            )

        logger.info(f"Deleted session {session_id} with {len(result.data)} messages")

        return StatusResponse(
            success=True,
            message=f"Session deleted successfully ({len(result.data)} messages removed)"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


# ============================================
# ADMIN ENDPOINTS (isteğe bağlı)
# ============================================

@router.get("/sessions/{chatbot_id}")
async def list_chatbot_sessions(
    chatbot_id: UUID,
    page: int = 1,
    size: int = 20,
    supabase = Depends(get_supabase_client)
):
    """
    Belirli bir chatbot'un tüm session'larını listele

    **ADMIN ENDPOINT** - Authentication gerekebilir

    **Kullanım:**
    - Admin dashboard'da tüm conversation'ları görüntüleme
    - Analytics ve raporlama
    """
    try:
        offset = (page - 1) * size

        # Session'ları grupla ve istatistikleri hesapla
        query = """
        SELECT
            session_id,
            chatbot_id,
            MIN(created_at) as first_message_at,
            MAX(created_at) as last_message_at,
            COUNT(*) as total_messages,
            AVG(CASE WHEN message_direction = 'outgoing' THEN processing_time_ms END) as avg_response_time_ms,
            AVG(CASE WHEN was_helpful IS NOT NULL THEN CASE WHEN was_helpful THEN 1.0 ELSE 0.0 END END) as satisfaction_rate
        FROM chat_messages
        WHERE chatbot_id = %s
        GROUP BY session_id, chatbot_id
        ORDER BY last_message_at DESC
        LIMIT %s OFFSET %s
        """

        # NOT: Supabase Python client RPC call gerektirebilir
        # Şimdilik basit query kullanıyoruz

        result = supabase.table("chat_messages").select(
            "session_id, created_at"
        ).eq("chatbot_id", str(chatbot_id)).order(
            "created_at", desc=True
        ).limit(size).range(offset, offset + size - 1).execute()

        # Session'ları unique yap
        sessions = {}
        if result.data:
            for msg in result.data:
                sid = msg["session_id"]
                if sid not in sessions:
                    sessions[sid] = {
                        "session_id": sid,
                        "first_message_at": msg["created_at"],
                        "last_message_at": msg["created_at"]
                    }
                else:
                    sessions[sid]["last_message_at"] = msg["created_at"]

        return {
            "sessions": list(sessions.values()),
            "total": len(sessions),
            "page": page,
            "size": size
        }

    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )
