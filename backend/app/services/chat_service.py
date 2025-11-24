"""
Chat Service
Chatbot mesajlaşma işlemlerini yöneten servis
"""
import logging
import time
from typing import Dict, Any, Optional, List
from uuid import UUID

from app.config import get_supabase_client
from app.services.embedding_service import embedding_service
from app.services.ai_usage_log_service import ai_usage_log_service

logger = logging.getLogger(__name__)


class ChatService:
    """Chatbot mesajlaşma servis sınıfı"""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def save_message(
        self,
        chatbot_id: str,
        session_id: str,
        message_direction: str,
        content: str,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        message_type: str = "text",
        conversation_id: Optional[str] = None,
        ai_model: Optional[str] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        processing_time_ms: Optional[int] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        error_code: Optional[str] = None,
        source_chunks: Optional[List[str]] = None,
        source_entry_id: Optional[str] = None,
        formatted_content: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parent_message_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mesajı veritabanına kaydet

        Args:
            chatbot_id: Chatbot ID
            session_id: Session ID
            message_direction: "incoming" veya "outgoing"
            content: Mesaj içeriği
            ... diğer parametreler

        Returns:
            Kaydedilen mesaj
        """
        try:
            message_data = {
                "chatbot_id": chatbot_id,
                "session_id": session_id,
                "message_direction": message_direction,
                "message_type": message_type,
                "content": content,
                "status": status
            }

            # Opsiyonel alanlar
            if conversation_id:
                message_data["conversation_id"] = conversation_id
            if user_id:
                message_data["user_id"] = user_id
            if client_ip:
                message_data["client_ip"] = client_ip
            if user_agent:
                message_data["user_agent"] = user_agent
            if ai_model:
                message_data["ai_model"] = ai_model
            if prompt_tokens is not None:
                message_data["prompt_tokens"] = prompt_tokens
            if completion_tokens is not None:
                message_data["completion_tokens"] = completion_tokens
            if total_tokens is not None:
                message_data["total_tokens"] = total_tokens
            if processing_time_ms is not None:
                message_data["processing_time_ms"] = processing_time_ms
            if error_message:
                message_data["error_message"] = error_message
            if error_code:
                message_data["error_code"] = error_code
            if source_chunks:
                message_data["source_chunks"] = source_chunks
            if source_entry_id:
                message_data["source_entry_id"] = source_entry_id
            if formatted_content:
                message_data["formatted_content"] = formatted_content
            if metadata:
                message_data["metadata"] = metadata
            if parent_message_id:
                message_data["parent_message_id"] = parent_message_id
            if thread_id:
                message_data["thread_id"] = thread_id

            result = self.supabase.table("chat_messages").insert(message_data).execute()

            if not result.data:
                logger.error("Failed to save message to database")
                return None

            logger.info(f"✅ Message saved: {message_direction} - {message_data.get('id')}")
            return result.data[0]

        except Exception as e:
            logger.error(f"❌ Error saving message: {e}")
            return None

    async def send_message(
        self,
        chatbot_id: str,
        user_message: str,
        session_id: str,
        user_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Kullanıcı mesajını al, AI yanıtı üret, her ikisini de kaydet

        Args:
            chatbot_id: Chatbot ID
            user_message: Kullanıcının mesajı
            session_id: Session ID
            user_id: User ID (opsiyonel, anonim kullanıcılar için None)
            client_ip: Client IP
            user_agent: User Agent
            conversation_id: Conversation ID (mevcut konuşmayı gruplamak için)
            metadata: Metadata

        Returns:
            {
                "user_message_id": "...",
                "bot_message_id": "...",
                "bot_response": "...",
                "processing_time_ms": 1234,
                "total_tokens": 100,
                "source_chunks": [...],
                "source_entry_id": "..."
            }
        """
        try:
            # 1. Kullanıcı mesajını kaydet
            user_message_record = await self.save_message(
                chatbot_id=chatbot_id,
                session_id=session_id,
                message_direction="incoming",
                content=user_message,
                user_id=user_id,
                client_ip=client_ip,
                user_agent=user_agent,
                conversation_id=conversation_id,
                metadata=metadata
            )

            if not user_message_record:
                raise Exception("Failed to save user message")

            user_message_id = user_message_record["id"]

            # 2. Chatbot config'ini al
            chatbot_result = self.supabase.table("chatbots").select("*").eq("id", chatbot_id).execute()

            if not chatbot_result.data:
                raise Exception(f"Chatbot not found: {chatbot_id}")

            chatbot_config = chatbot_result.data[0]

            # 3. Conversation history'yi al (context için)
            history_result = self.supabase.table("chat_messages").select(
                "content, message_direction"
            ).eq("chatbot_id", chatbot_id).eq("session_id", session_id).order(
                "created_at", desc=False
            ).limit(10).execute()

            conversation_history = []
            if history_result.data:
                for msg in history_result.data[:-1]:  # Son mesajı (user'ın yeni mesajını) hariç tut
                    role = "user" if msg["message_direction"] == "incoming" else "assistant"
                    conversation_history.append({
                        "role": role,
                        "content": msg["content"]
                    })

            # 4. Knowledge base'den context bul (embedding search)
            context = []
            try:
                # TODO: Embedding search ile ilgili chunk'ları bul
                # Şimdilik basit keyword search yapabiliriz
                chunks_result = self.supabase.table("knowledge_chunks").select(
                    "id, content, knowledge_entry_id"
                ).eq("chatbot_id", chatbot_id).limit(5).execute()

                if chunks_result.data:
                    context = chunks_result.data
            except Exception as e:
                logger.warning(f"Failed to fetch context chunks: {e}")

            # 5. AI yanıtı üret
            start_time = time.time()

            bot_response_data = await embedding_service.generate_ai_response(
                user_message=user_message,
                context=context,
                chatbot_config=chatbot_config,
                conversation_id=user_message_id,
                chatbot_id=chatbot_id
            )

            processing_time_ms = int((time.time() - start_time) * 1000)

            # 6. Bot yanıtını kaydet
            source_chunks = [chunk["id"] for chunk in context] if context else []
            source_entry_id = context[0].get("knowledge_entry_id") if context else None

            bot_message_record = await self.save_message(
                chatbot_id=chatbot_id,
                session_id=session_id,
                message_direction="outgoing",
                content=bot_response_data,
                conversation_id=conversation_id,
                ai_model="openrouter",  # TODO: Dinamik olarak al
                processing_time_ms=processing_time_ms,
                source_chunks=source_chunks,
                source_entry_id=source_entry_id,
                parent_message_id=user_message_id
            )

            if not bot_message_record:
                raise Exception("Failed to save bot message")

            bot_message_id = bot_message_record["id"]

            logger.info(f"✅ Chat completed: user_msg={user_message_id}, bot_msg={bot_message_id}")

            return {
                "success": True,
                "user_message_id": user_message_id,
                "bot_message_id": bot_message_id,
                "bot_response": bot_response_data,
                "processing_time_ms": processing_time_ms,
                "total_tokens": None,  # TODO: Token bilgisini al
                "source_chunks": source_chunks,
                "source_entry_id": source_entry_id,
                "session_id": session_id
            }

        except Exception as e:
            logger.error(f"❌ Error in send_message: {e}")

            # Hata mesajı kaydet
            await self.save_message(
                chatbot_id=chatbot_id,
                session_id=session_id,
                message_direction="outgoing",
                content=f"Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.",
                status="failed",
                error_message=str(e),
                error_code="internal_error"
            )

            raise

    async def get_conversation_history(
        self,
        session_id: str,
        chatbot_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Belirli bir session'ın mesaj geçmişini getir

        Args:
            session_id: Session ID
            chatbot_id: Chatbot ID
            limit: Maksimum mesaj sayısı

        Returns:
            Mesaj listesi
        """
        try:
            result = self.supabase.table("chat_messages").select("*").eq(
                "session_id", session_id
            ).eq("chatbot_id", chatbot_id).order(
                "created_at", desc=False
            ).limit(limit).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"❌ Error fetching conversation history: {e}")
            return []

    async def update_feedback(
        self,
        message_id: str,
        was_helpful: Optional[bool] = None,
        sentiment: Optional[str] = None,
        user_feedback: Optional[str] = None,
        feedback_rating: Optional[int] = None
    ) -> bool:
        """
        Mesaj geri bildirimini güncelle

        Args:
            message_id: Message ID
            was_helpful: Yardımcı oldu mu?
            sentiment: Duygu (positive, negative, neutral)
            user_feedback: Kullanıcı yorumu
            feedback_rating: Puan (1-5)

        Returns:
            Başarılı oldu mu?
        """
        try:
            update_data = {}

            if was_helpful is not None:
                update_data["was_helpful"] = was_helpful
            if sentiment:
                update_data["sentiment"] = sentiment
            if user_feedback:
                update_data["user_feedback"] = user_feedback
            if feedback_rating:
                update_data["feedback_rating"] = feedback_rating

            if not update_data:
                return False

            result = self.supabase.table("chat_messages").update(update_data).eq("id", message_id).execute()

            return bool(result.data)

        except Exception as e:
            logger.error(f"❌ Error updating feedback: {e}")
            return False


# Singleton instance
chat_service = ChatService()
