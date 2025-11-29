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
    ConversationHistoryResponse,
    SessionWithMessages,
    UserChatbotMessagesResponse,
    PaginationInfo
)
from app.schemas.common import StatusResponse
from app.dependencies import get_supabase_client, get_current_user
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


# ============================================
# USER-CHATBOT MESSAGES ENDPOINT
# ============================================

@router.get("/chatbots/{chatbot_id}/messages", response_model=UserChatbotMessagesResponse)
async def get_chatbot_user_messages(
    chatbot_id: UUID,
    user_id: Optional[UUID] = None,
    session_id: Optional[str] = None,
    page: int = 1,
    size: int = 50,
    group_by_session: bool = True,
    include_visitor_info: bool = True,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Belirli bir chatbot'un kullanıcı mesajlarını getir

    **Kullanım:**
    - Kullanıcının belirli bir chatbot ile yaptığı tüm konuşmaları görüntüleme
    - Session bazlı gruplama ile organize edilmiş mesajlar
    - Ziyaretçi ID (MM00001) bilgisi dahil

    **Query Parameters:**
    - user_id: Belirli kullanıcının mesajları (opsiyonel)
    - session_id: Belirli session'ın mesajları (opsiyonel)
    - page: Sayfa numarası (varsayılan: 1)
    - size: Sayfa başına kayıt (varsayılan: 50, max: 100)
    - group_by_session: Session bazlı gruplama (varsayılan: true)
    - include_visitor_info: Ziyaretçi ID bilgisi ekle (varsayılan: true)

    **Authorization:**
    - Chatbot kullanıcıya ait olmalı
    - Sadece kendi chatbot'larının mesajlarını görebilir
    """
    try:
        # Validate page and size
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be >= 1")
        if size < 1 or size > 100:
            raise HTTPException(status_code=400, detail="Size must be between 1 and 100")

        # 1. Chatbot ownership kontrolü
        chatbot_result = supabase.table("chatbots").select(
            "id, name, user_id"
        ).eq("id", str(chatbot_id)).execute()

        if not chatbot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )

        chatbot = chatbot_result.data[0]

        # Chatbot'un user'a ait olduğunu kontrol et
        if chatbot["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this chatbot's messages"
            )

        offset = (page - 1) * size

        if group_by_session:
            # ============================================
            # SESSION BAZLI GRUPLAMA
            # ============================================

            # 1. Session'ları bul ve grupla
            sessions_query = supabase.table("chat_messages").select(
                "session_id, created_at, processing_time_ms, was_helpful, message_direction"
            ).eq("chatbot_id", str(chatbot_id))

            # User ID filtresi
            if user_id:
                sessions_query = sessions_query.eq("user_id", str(user_id))

            # Session ID filtresi
            if session_id:
                sessions_query = sessions_query.eq("session_id", session_id)

            sessions_result = sessions_query.execute()

            if not sessions_result.data:
                return UserChatbotMessagesResponse(
                    chatbot_id=chatbot_id,
                    user_id=user_id,
                    total_sessions=0,
                    total_messages=0,
                    sessions=[],
                    pagination=PaginationInfo(
                        page=page,
                        size=size,
                        total=0,
                        total_pages=0
                    )
                )

            # Session'ları grupla
            sessions_dict = {}
            for msg in sessions_result.data:
                sid = msg["session_id"]
                if sid not in sessions_dict:
                    sessions_dict[sid] = {
                        "session_id": sid,
                        "first_message_at": msg["created_at"],
                        "last_message_at": msg["created_at"],
                        "message_count": 0,
                        "user_message_count": 0,
                        "bot_message_count": 0,
                        "response_times": [],
                        "helpful_votes": []
                    }

                sessions_dict[sid]["message_count"] += 1
                sessions_dict[sid]["last_message_at"] = max(
                    sessions_dict[sid]["last_message_at"],
                    msg["created_at"]
                )
                sessions_dict[sid]["first_message_at"] = min(
                    sessions_dict[sid]["first_message_at"],
                    msg["created_at"]
                )

                if msg["message_direction"] == "incoming":
                    sessions_dict[sid]["user_message_count"] += 1
                elif msg["message_direction"] == "outgoing":
                    sessions_dict[sid]["bot_message_count"] += 1
                    if msg.get("processing_time_ms"):
                        sessions_dict[sid]["response_times"].append(msg["processing_time_ms"])

                if msg.get("was_helpful") is not None:
                    sessions_dict[sid]["helpful_votes"].append(1 if msg["was_helpful"] else 0)

            # Session'ları tarihe göre sırala
            sorted_sessions = sorted(
                sessions_dict.values(),
                key=lambda x: x["last_message_at"],
                reverse=True
            )

            total_sessions = len(sorted_sessions)
            total_messages = sum(s["message_count"] for s in sorted_sessions)

            # Pagination uygula
            paginated_sessions = sorted_sessions[offset:offset + size]

            # 2. Her session için mesajları ve ziyaretçi bilgisini al
            sessions_with_messages = []

            for session_info in paginated_sessions:
                sid = session_info["session_id"]

                # Ziyaretçi bilgisini al (eğer isteniyorsa)
                ziyaretci_id = None
                if include_visitor_info:
                    visitor_result = supabase.table("session_visitors").select(
                        "ziyaretci_id"
                    ).eq("session_id", sid).execute()

                    if visitor_result.data:
                        ziyaretci_id = visitor_result.data[0]["ziyaretci_id"]

                # Session'ın tüm mesajlarını al
                messages_result = supabase.table("chat_messages").select(
                    "*"
                ).eq("chatbot_id", str(chatbot_id)).eq("session_id", sid).order(
                    "created_at", desc=False
                ).execute()

                messages = []
                if messages_result.data:
                    for msg in messages_result.data:
                        # source_chunks'ı list'e çevir
                        if isinstance(msg.get("source_chunks"), str):
                            msg["source_chunks"] = []
                        elif msg.get("source_chunks") is None:
                            msg["source_chunks"] = []

                        # metadata'yı dict'e çevir
                        if msg.get("metadata") is None:
                            msg["metadata"] = {}

                        messages.append(ChatMessageResponse(**msg))

                # İstatistikleri hesapla
                avg_response_time = None
                if session_info["response_times"]:
                    avg_response_time = sum(session_info["response_times"]) / len(session_info["response_times"])

                satisfaction_rate = None
                if session_info["helpful_votes"]:
                    satisfaction_rate = sum(session_info["helpful_votes"]) / len(session_info["helpful_votes"])

                sessions_with_messages.append(SessionWithMessages(
                    session_id=sid,
                    ziyaretci_id=ziyaretci_id,
                    first_message_at=session_info["first_message_at"],
                    last_message_at=session_info["last_message_at"],
                    message_count=session_info["message_count"],
                    user_message_count=session_info["user_message_count"],
                    bot_message_count=session_info["bot_message_count"],
                    avg_response_time_ms=avg_response_time,
                    satisfaction_rate=satisfaction_rate,
                    messages=messages
                ))

            return UserChatbotMessagesResponse(
                chatbot_id=chatbot_id,
                user_id=user_id,
                total_sessions=total_sessions,
                total_messages=total_messages,
                sessions=sessions_with_messages,
                pagination=PaginationInfo(
                    page=page,
                    size=size,
                    total=total_sessions,
                    total_pages=(total_sessions + size - 1) // size
                )
            )

        else:
            # ============================================
            # DÜZ LİSTE (Groupsuz)
            # ============================================

            # Toplam sayıyı al
            count_query = supabase.table("chat_messages").select(
                "id", count="exact"
            ).eq("chatbot_id", str(chatbot_id))

            if user_id:
                count_query = count_query.eq("user_id", str(user_id))
            if session_id:
                count_query = count_query.eq("session_id", session_id)

            count_result = count_query.execute()
            total = count_result.count if count_result.count else 0

            # Mesajları al
            messages_query = supabase.table("chat_messages").select(
                "*"
            ).eq("chatbot_id", str(chatbot_id))

            if user_id:
                messages_query = messages_query.eq("user_id", str(user_id))
            if session_id:
                messages_query = messages_query.eq("session_id", session_id)

            messages_result = messages_query.order(
                "created_at", desc=True
            ).range(offset, offset + size - 1).execute()

            messages = []
            if messages_result.data:
                for msg in messages_result.data:
                    # source_chunks'ı list'e çevir
                    if isinstance(msg.get("source_chunks"), str):
                        msg["source_chunks"] = []
                    elif msg.get("source_chunks") is None:
                        msg["source_chunks"] = []

                    # metadata'yı dict'e çevir
                    if msg.get("metadata") is None:
                        msg["metadata"] = {}

                    # Ziyaretçi bilgisini ekle
                    if include_visitor_info and msg.get("session_id"):
                        visitor_result = supabase.table("session_visitors").select(
                            "ziyaretci_id"
                        ).eq("session_id", msg["session_id"]).execute()

                        if visitor_result.data:
                            msg["ziyaretci_id"] = visitor_result.data[0]["ziyaretci_id"]

                    messages.append(ChatMessageResponse(**msg))

            return UserChatbotMessagesResponse(
                chatbot_id=chatbot_id,
                user_id=user_id,
                total_sessions=None,
                total_messages=total,
                messages=messages,
                pagination=PaginationInfo(
                    page=page,
                    size=size,
                    total=total,
                    total_pages=(total + size - 1) // size
                )
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chatbot user messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}"
        )
