"""
Chunk Enrichment Service
AI ile chunk'ları zenginleştirme servisi
"""
import json
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
import httpx
import asyncio

from app.config.settings import settings
from app.database import get_supabase_client
from app.services.ai_usage_log_service import ai_usage_log_service

logger = logging.getLogger(__name__)


class ChunkEnrichmentService:
    """
    AI ile chunk'ları zenginleştirme servisi
    - Özet çıkarma
    - Tag oluşturma
    - Metadata ekleme
    """

    # AI Enrichment Prompt Template - İyileştirilmiş Versiyon
    ENRICHMENT_PROMPT = """Sen bir metin analiz uzmanısın. Aşağıdaki metin parçasını detaylı şekilde analiz et ve JSON formatında veri çıkar.

=== METİN ===
{chunk_content}

=== GÖREVLER ===

1. ÖZET (summary):
   - Metnin ana fikrini 1-2 cümleyle özetle
   - Açık ve anlaşılır Türkçe kullan
   - Teknik terimleri basitleştirme
   - Okuyucuya metnin ne hakkında olduğunu net şekilde anlat

2. ETİKETLER (tags):
   - 3-5 adet anahtar kelime/etiket bul
   - Arama motorlarında kullanılabilecek kelimeler seç
   - Teknik terimleri dahil et
   - İngilizce ve Türkçe karışık olabilir
   - Örnekler: "AI", "Makine Öğrenmesi", "Sağlık", "Finans"

3. ANA KAVRAMLAR (key_concepts):
   - Metinde geçen önemli kavram, terim ve konuları listele
   - 3-7 adet kavram çıkar
   - Spesifik olmalı (örn: "veri" yerine "veri analizi")
   - Kişi adları, teknoloji isimleri, özel terimler dahil edilmeli

4. KARMAŞIKLIK SEVİYESİ (complexity_level):
   - "beginner": Herkesin anlayabileceği basit metin
   - "intermediate": Orta seviye bilgi gerektiren metin
   - "advanced": Uzmanlık gerektiren teknik/karmaşık metin

5. DİL KODU (language):
   - Metnin yazıldığı dil kodu (tr, en, de, fr, es, ar, vb.)
   - Karışık dillerde baskın olan dili seç

=== ÖNEMLİ KURALLAR ===
- SADECE JSON formatında cevap ver, başka hiçbir metin ekleme
- Tırnak işaretlerini doğru kullan
- Türkçe karakterleri koru (ı, ş, ğ, ü, ö, ç, İ)
- Eğer metin çok kısa veya anlamsızsa yine de tahmin yap

=== CEVAP FORMATI ===
{{
  "summary": "Metnin ana fikrini açıklayan 1-2 cümle...",
  "tags": ["etiket1", "etiket2", "etiket3", "etiket4"],
  "key_concepts": ["kavram1", "kavram2", "kavram3"],
  "complexity_level": "intermediate",
  "language": "tr"
}}

ŞİMDİ ANALİZ ET:"""

    def __init__(self):
        self.supabase = get_supabase_client()
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.default_model = settings.GEMINI_MODEL

    async def create_enrichment_job(
        self,
        knowledge_entry_id: str,
        chatbot_id: Optional[str],
        user_id: str,
        prompt_template: Optional[str] = None,
        ai_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Yeni bir enrichment job'ı oluşturur

        Args:
            knowledge_entry_id: Knowledge base entry ID
            chatbot_id: Chatbot ID
            user_id: User ID
            prompt_template: Özel prompt template (opsiyonel)
            ai_model: AI model (opsiyonel)

        Returns:
            Oluşturulan job bilgisi
        """
        try:
            # Chunk sayısını al
            chunks_result = self.supabase.table("knowledge_chunks").select(
                "id", count="exact"
            ).eq("knowledge_entry_id", knowledge_entry_id).execute()

            total_chunks = chunks_result.count or 0

            if total_chunks == 0:
                raise ValueError("No chunks found for this knowledge entry")

            # Job oluştur
            job_data = {
                "knowledge_entry_id": knowledge_entry_id,
                "chatbot_id": chatbot_id,
                "user_id": user_id,
                "status": "pending",
                "total_chunks": total_chunks,
                "processed_chunks": 0,
                "failed_chunks": 0,
                "prompt_template": prompt_template,
                "ai_model": ai_model or self.default_model
            }

            result = self.supabase.table("chunk_enrichment_jobs").insert(job_data).execute()

            if not result.data:
                raise Exception("Failed to create enrichment job")

            logger.info(f"Created enrichment job: {result.data[0]['id']}")
            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to create enrichment job: {e}")
            raise

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Job durumunu getirir

        Args:
            job_id: Job ID

        Returns:
            Job durumu veya None
        """
        try:
            result = self.supabase.table("chunk_enrichment_jobs").select("*").eq(
                "id", job_id
            ).execute()

            if result.data and len(result.data) > 0:
                job = result.data[0]

                # Progress hesapla
                percentage = 0
                if job['total_chunks'] > 0:
                    percentage = (job['processed_chunks'] / job['total_chunks']) * 100

                return {
                    **job,
                    "progress": {
                        "total_chunks": job['total_chunks'],
                        "processed_chunks": job['processed_chunks'],
                        "failed_chunks": job['failed_chunks'],
                        "percentage": round(percentage, 2)
                    }
                }

            return None

        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return None

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        error_message: Optional[str] = None
    ):
        """Job durumunu günceller"""
        try:
            update_data = {"status": status, "updated_at": datetime.utcnow().isoformat()}

            if status == "processing" and not error_message:
                update_data["started_at"] = datetime.utcnow().isoformat()
            elif status in ["completed", "failed"]:
                update_data["completed_at"] = datetime.utcnow().isoformat()

            if error_message:
                update_data["error_message"] = error_message

            self.supabase.table("chunk_enrichment_jobs").update(update_data).eq(
                "id", job_id
            ).execute()

            logger.info(f"Updated job {job_id} status to {status}")

        except Exception as e:
            logger.error(f"Failed to update job status: {e}")

    async def increment_processed_count(self, job_id: str):
        """İşlenen chunk sayısını artırır"""
        try:
            # Önce mevcut değeri al
            job = await self.get_job_status(job_id)
            if job:
                new_count = job['processed_chunks'] + 1
                self.supabase.table("chunk_enrichment_jobs").update({
                    "processed_chunks": new_count,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", job_id).execute()

        except Exception as e:
            logger.error(f"Failed to increment processed count: {e}")

    async def increment_failed_count(self, job_id: str):
        """Başarısız chunk sayısını artırır"""
        try:
            # Önce mevcut değeri al
            job = await self.get_job_status(job_id)
            if job:
                new_count = job['failed_chunks'] + 1
                self.supabase.table("chunk_enrichment_jobs").update({
                    "failed_chunks": new_count,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", job_id).execute()

        except Exception as e:
            logger.error(f"Failed to increment failed count: {e}")

    async def enrich_single_chunk(
        self,
        chunk_content: str,
        prompt_template: Optional[str] = None,
        ai_model: Optional[str] = None,
        chunk_id: Optional[str] = None,
        knowledge_entry_id: Optional[str] = None,
        chatbot_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tek bir chunk'ı Google Gemini AI ile zenginleştirir

        Args:
            chunk_content: Chunk içeriği
            prompt_template: Özel prompt (opsiyonel)
            ai_model: AI model (opsiyonel)
            chunk_id: Chunk ID (loglama için)
            knowledge_entry_id: Knowledge entry ID (loglama için)
            chatbot_id: Chatbot ID (loglama için)
            user_id: User ID (loglama için)

        Returns:
            Zenginleştirilmiş veri
        """
        start_time = datetime.utcnow()
        input_prompt = None
        ai_response = None

        try:
            # Prompt validation - "string" gibi placeholder değerleri temizle
            if prompt_template and prompt_template.strip().lower() == "string":
                prompt_template = None

            # Model validation - "string" gibi geçersiz değerleri temizle
            if ai_model and (ai_model.strip().lower() == "string" or not ai_model.strip()):
                ai_model = None

            # Prompt oluştur
            prompt = (prompt_template or self.ENRICHMENT_PROMPT).format(
                chunk_content=chunk_content[:4000]  # Gemini daha uzun içerik destekler
            )
            input_prompt = prompt  # Loglama için kaydet

            model_name = ai_model or self.default_model

            # Google Gemini API'ye istek gönder
            async with httpx.AsyncClient(timeout=60.0) as client:
                api_start_time = datetime.utcnow()

                response = await client.post(
                    f"{self.base_url}/models/{model_name}:generateContent",
                    params={"key": self.api_key},
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{
                                "text": prompt
                            }]
                        }],
                        "generationConfig": {
                            "temperature": 0.3,  # Daha tutarlı sonuçlar
                            "topK": 40,
                            "topP": 0.95,
                            "maxOutputTokens": 1024,
                        }
                    }
                )

                api_end_time = datetime.utcnow()
                latency_ms = int((api_end_time - api_start_time).total_seconds() * 1000)

                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"Gemini API error: {response.status_code} - {error_detail}")

                    # ❌ Başarısız isteği logla
                    await ai_usage_log_service.log_ai_request(
                        usage_type="chunk_enrichment",
                        model_name=model_name,
                        input_text=input_prompt[:5000],  # Çok uzun metinleri kısalt
                        output_text=None,
                        latency_ms=latency_ms,
                        status="failed",
                        chunk_id=chunk_id,
                        knowledge_entry_id=knowledge_entry_id,
                        chatbot_id=chatbot_id,
                        user_id=user_id,
                        error_message=f"API error: {response.status_code}",
                        metadata={
                            "temperature": 0.3,
                            "topK": 40,
                            "topP": 0.95,
                            "maxOutputTokens": 1024
                        }
                    )

                    raise Exception(f"Gemini API error: {response.status_code}")

                result = response.json()

                # Token bilgilerini çek
                usage_metadata = result.get("usageMetadata", {})
                input_tokens = usage_metadata.get("promptTokenCount", 0)
                output_tokens = usage_metadata.get("candidatesTokenCount", 0)
                total_tokens = usage_metadata.get("totalTokenCount", 0)

                # Gemini response formatı
                if "candidates" in result and len(result["candidates"]) > 0:
                    ai_response = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                else:
                    # ❌ Response yok hatası
                    await ai_usage_log_service.log_ai_request(
                        usage_type="chunk_enrichment",
                        model_name=model_name,
                        input_text=input_prompt[:5000],
                        output_text=None,
                        latency_ms=latency_ms,
                        status="failed",
                        chunk_id=chunk_id,
                        knowledge_entry_id=knowledge_entry_id,
                        chatbot_id=chatbot_id,
                        user_id=user_id,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        total_tokens=total_tokens,
                        error_message="No response from Gemini",
                        metadata={
                            "temperature": 0.3,
                            "topK": 40,
                            "topP": 0.95,
                            "maxOutputTokens": 1024
                        }
                    )
                    raise Exception("No response from Gemini")

                # JSON parse et
                # Gemini bazen markdown code block içinde döndürür: ```json ... ```
                ai_response = ai_response.replace("```json", "").replace("```", "").strip()

                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1

                if json_start != -1 and json_end > json_start:
                    json_str = ai_response[json_start:json_end]
                    enrichment_data = json.loads(json_str)
                else:
                    # Fallback
                    enrichment_data = {
                        "summary": "Özet oluşturulamadı",
                        "tags": [],
                        "key_concepts": [],
                        "complexity_level": "intermediate",
                        "language": "tr"
                    }

                # Zenginleştirme zamanını ekle
                enrichment_data["enriched_at"] = datetime.utcnow().isoformat()

                # ✅ Başarılı isteği logla (token bilgileriyle)
                await ai_usage_log_service.log_ai_request(
                    usage_type="chunk_enrichment",
                    model_name=model_name,
                    input_text=input_prompt[:5000],  # Çok uzun metinleri kısalt
                    output_text=ai_response[:5000],
                    latency_ms=latency_ms,
                    status="success",
                    chunk_id=chunk_id,
                    knowledge_entry_id=knowledge_entry_id,
                    chatbot_id=chatbot_id,
                    user_id=user_id,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    metadata={
                        "temperature": 0.3,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 1024,
                        "enrichment_summary": enrichment_data.get("summary", "")[:200]
                    }
                )

                logger.info("Chunk successfully enriched with Gemini")
                return enrichment_data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")

            # JSON parse hatası da loglanmalı
            end_time = datetime.utcnow()
            latency_ms = int((end_time - start_time).total_seconds() * 1000)

            await ai_usage_log_service.log_ai_request(
                usage_type="chunk_enrichment",
                model_name=ai_model or self.default_model,
                input_text=(input_prompt or "")[:5000],
                output_text=(ai_response or "")[:5000],
                latency_ms=latency_ms,
                status="failed",
                chunk_id=chunk_id,
                knowledge_entry_id=knowledge_entry_id,
                chatbot_id=chatbot_id,
                user_id=user_id,
                error_message=f"JSON parse error: {str(e)[:200]}",
                metadata={"error_type": "json_parse_error"}
            )

            return {
                "summary": "JSON parse hatası",
                "tags": [],
                "key_concepts": [],
                "complexity_level": "unknown",
                "language": "tr",
                "enriched_at": datetime.utcnow().isoformat(),
                "error": "JSON parse failed"
            }
        except Exception as e:
            logger.error(f"Failed to enrich chunk: {e}")

            # Genel hataları logla
            end_time = datetime.utcnow()
            latency_ms = int((end_time - start_time).total_seconds() * 1000)

            await ai_usage_log_service.log_ai_request(
                usage_type="chunk_enrichment",
                model_name=ai_model or self.default_model,
                input_text=(input_prompt or "")[:5000],
                output_text=(ai_response or "")[:5000],
                latency_ms=latency_ms,
                status="failed",
                chunk_id=chunk_id,
                knowledge_entry_id=knowledge_entry_id,
                chatbot_id=chatbot_id,
                user_id=user_id,
                error_message=str(e)[:500],
                metadata={"error_type": "general_error"}
            )

            # Fallback data
            return {
                "summary": f"Hata: {str(e)[:100]}",
                "tags": [],
                "key_concepts": [],
                "complexity_level": "unknown",
                "language": "tr",
                "enriched_at": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    async def enrich_all_chunks_background(
        self,
        job_id: str,
        knowledge_entry_id: str,
        prompt_template: Optional[str] = None,
        ai_model: Optional[str] = None,
        chatbot_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        Arka planda tüm chunk'ları zenginleştirir

        Args:
            job_id: Job ID
            knowledge_entry_id: Knowledge entry ID
            prompt_template: Özel prompt
            ai_model: AI model
        """
        try:
            logger.info(f"Starting background enrichment for job {job_id}")

            # Job'u processing olarak işaretle
            await self.update_job_status(job_id, "processing")

            # Chunk'ları al
            chunks_result = self.supabase.table("knowledge_chunks").select(
                "id, chunk_index, content, metadata"
            ).eq("knowledge_entry_id", knowledge_entry_id).order("chunk_index").execute()

            if not chunks_result.data:
                await self.update_job_status(job_id, "failed", "No chunks found")
                return

            chunks = chunks_result.data
            logger.info(f"Processing {len(chunks)} chunks")

            # Her chunk'ı işle
            for chunk in chunks:
                try:
                    # AI ile zenginleştir (loglama parametreleriyle)
                    enrichment_data = await self.enrich_single_chunk(
                        chunk['content'],
                        prompt_template,
                        ai_model,
                        chunk_id=chunk['id'],
                        knowledge_entry_id=knowledge_entry_id,
                        chatbot_id=chatbot_id,
                        user_id=user_id
                    )

                    # Mevcut metadata'yı al
                    existing_metadata = chunk.get('metadata', {})
                    if isinstance(existing_metadata, str):
                        existing_metadata = json.loads(existing_metadata)

                    # Enrichment'ı metadata'ya ekle
                    updated_metadata = {
                        **existing_metadata,
                        "enrichment": enrichment_data
                    }

                    # Chunk'ı güncelle
                    self.supabase.table("knowledge_chunks").update({
                        "metadata": updated_metadata,
                        "updated_at": datetime.utcnow().isoformat()
                    }).eq("id", chunk['id']).execute()

                    # Progress güncelle
                    await self.increment_processed_count(job_id)

                    logger.info(f"Enriched chunk {chunk['chunk_index']}")

                    # Rate limiting - Gemini free tier: 15 RPM (4 saniye = dakikada 15 request)
                    await asyncio.sleep(4)

                except Exception as e:
                    logger.error(f"Failed to enrich chunk {chunk['id']}: {e}")
                    await self.increment_failed_count(job_id)

            # Job'u tamamla
            await self.update_job_status(job_id, "completed")
            logger.info(f"Enrichment job {job_id} completed")

        except Exception as e:
            logger.error(f"Background enrichment failed: {e}")
            await self.update_job_status(job_id, "failed", str(e))


# Global instance
chunk_enrichment_service = ChunkEnrichmentService()
