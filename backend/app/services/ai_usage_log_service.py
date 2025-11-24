"""
AI Usage Log Service
AI isteklerini loglama servisi
"""
import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.database import get_supabase_client
from app.schemas.ai_usage_log import AIUsageLogCreate

logger = logging.getLogger(__name__)


class AIUsageLogService:
    """
    AI kullanım loglarını yöneten servis
    """

    def __init__(self):
        self.supabase = get_supabase_client()

    async def log_ai_request(
        self,
        usage_type: str,
        model_name: str,
        input_text: str,
        output_text: Optional[str],
        latency_ms: int,
        status: str = "success",
        chunk_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        knowledge_entry_id: Optional[str] = None,
        chatbot_id: Optional[str] = None,
        user_id: Optional[str] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        AI isteğini loglar

        Args:
            usage_type: Kullanım tipi (chunk_enrichment, chat_response, vb.)
            model_name: Kullanılan AI model
            input_text: Input metni
            output_text: Output metni
            latency_ms: İstek süresi (milisaniye)
            status: İstek durumu (success, failed, timeout, rate_limited)
            chunk_id: İlgili chunk ID (opsiyonel)
            conversation_id: İlgili conversation ID (opsiyonel)
            knowledge_entry_id: İlgili knowledge entry ID (opsiyonel)
            chatbot_id: İlgili chatbot ID (opsiyonel)
            user_id: İsteği başlatan kullanıcı ID (opsiyonel)
            input_tokens: Input token sayısı (opsiyonel)
            output_tokens: Output token sayısı (opsiyonel)
            total_tokens: Toplam token sayısı (opsiyonel)
            error_message: Hata mesajı (opsiyonel)
            metadata: Ek metadata (opsiyonel)

        Returns:
            Oluşturulan log kaydı veya None
        """
        try:
            log_data = {
                "usage_type": usage_type,
                "model_name": model_name,
                "input_text": input_text,
                "output_text": output_text,
                "latency_ms": latency_ms,
                "status": status,
                "chunk_id": chunk_id,
                "conversation_id": conversation_id,
                "knowledge_entry_id": knowledge_entry_id,
                "chatbot_id": chatbot_id,
                "user_id": user_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "error_message": error_message,
                "metadata": metadata or {}
            }

            result = self.supabase.table("ai_usage_logs").insert(log_data).execute()

            if result.data and len(result.data) > 0:
                logger.info(f"AI usage logged: {usage_type} - {model_name} - {latency_ms}ms")
                return result.data[0]

            logger.warning("AI usage log insertion returned no data")
            return None

        except Exception as e:
            logger.error(f"Failed to log AI usage: {e}")
            # Loglama hatası ana akışı bozmamalı
            return None

    async def get_usage_stats(
        self,
        chatbot_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        AI kullanım istatistiklerini getirir

        Args:
            chatbot_id: Chatbot ID filtresi (opsiyonel)
            user_id: User ID filtresi (opsiyonel)
            start_date: Başlangıç tarihi (opsiyonel)
            end_date: Bitiş tarihi (opsiyonel)

        Returns:
            Kullanım istatistikleri
        """
        try:
            query = self.supabase.table("ai_usage_logs").select("*")

            if chatbot_id:
                query = query.eq("chatbot_id", chatbot_id)
            if user_id:
                query = query.eq("user_id", user_id)
            if start_date:
                query = query.gte("created_at", start_date.isoformat())
            if end_date:
                query = query.lte("created_at", end_date.isoformat())

            result = query.execute()

            logs = result.data if result.data else []

            # İstatistikleri hesapla
            total_requests = len(logs)
            successful_requests = sum(1 for log in logs if log.get("status") == "success")
            failed_requests = sum(1 for log in logs if log.get("status") in ["failed", "timeout", "rate_limited"])

            total_tokens = sum(log.get("total_tokens", 0) or 0 for log in logs)
            total_latency = sum(log.get("latency_ms", 0) or 0 for log in logs)
            avg_latency = total_latency / total_requests if total_requests > 0 else 0

            # Usage type dağılımı
            by_usage_type = {}
            for log in logs:
                usage_type = log.get("usage_type", "unknown")
                by_usage_type[usage_type] = by_usage_type.get(usage_type, 0) + 1

            # Model dağılımı
            by_model = {}
            for log in logs:
                model = log.get("model_name", "unknown")
                by_model[model] = by_model.get(model, 0) + 1

            return {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "total_tokens": total_tokens,
                "avg_latency_ms": round(avg_latency, 2),
                "by_usage_type": by_usage_type,
                "by_model": by_model,
                "total_cost": 0.0  # TODO: Model bazlı maliyet hesabı
            }

        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_tokens": 0,
                "avg_latency_ms": 0,
                "by_usage_type": {},
                "by_model": {},
                "total_cost": 0.0,
                "error": str(e)
            }

    async def get_recent_logs(
        self,
        limit: int = 50,
        chatbot_id: Optional[str] = None,
        usage_type: Optional[str] = None
    ) -> list:
        """
        Son AI loglarını getirir

        Args:
            limit: Maksimum kayıt sayısı
            chatbot_id: Chatbot ID filtresi (opsiyonel)
            usage_type: Usage type filtresi (opsiyonel)

        Returns:
            Log listesi
        """
        try:
            query = self.supabase.table("ai_usage_logs").select("*")

            if chatbot_id:
                query = query.eq("chatbot_id", chatbot_id)
            if usage_type:
                query = query.eq("usage_type", usage_type)

            query = query.order("created_at", desc=True).limit(limit)
            result = query.execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to get recent logs: {e}")
            return []


# Global instance
ai_usage_log_service = AIUsageLogService()
