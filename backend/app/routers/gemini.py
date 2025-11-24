"""
Gemini AI Test Router
Gemini AI bağlantı testi ve sağlık kontrolü
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import logging
from typing import Dict, Any
from app.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gemini", tags=["Gemini AI"])


class GeminiTestResponse(BaseModel):
    """Gemini test yanıt modeli"""
    success: bool
    message: str
    model: str
    details: Dict[str, Any]


@router.get("/test-connection", response_model=GeminiTestResponse)
async def test_gemini_connection():
    """
    Gemini AI bağlantısını test et

    Returns:
        GeminiTestResponse: Bağlantı test sonucu
    """
    try:
        logger.info("🔍 Gemini AI bağlantı testi başlatılıyor...")

        # API key kontrolü
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.error("❌ GEMINI_API_KEY bulunamadı!")
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY environment variable tanımlı değil"
            )

        # Model kontrolü
        model_name = settings.GEMINI_MODEL
        logger.info(f"🤖 Model: {model_name}")

        # Gemini yapılandırması
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        # Basit test mesajı gönder
        test_prompt = "Merhaba, bağlantı testi. Sadece 'OK' yaz."
        logger.info(f"📤 Test mesajı gönderiliyor: {test_prompt}")

        response = model.generate_content(test_prompt)

        if response and response.text:
            logger.info(f"✅ Gemini AI yanıt verdi: {response.text[:50]}...")

            return GeminiTestResponse(
                success=True,
                message="Gemini AI bağlantısı başarılı!",
                model=model_name,
                details={
                    "api_key_status": "✅ Tanımlı",
                    "model_status": "✅ Erişilebilir",
                    "response_preview": response.text[:100],
                    "test_status": "✅ Başarılı"
                }
            )
        else:
            logger.warning("⚠️ Gemini AI yanıt vermedi")
            raise HTTPException(
                status_code=500,
                detail="Gemini AI'dan yanıt alınamadı"
            )

    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Gemini AI bağlantı hatası: {error_msg}")

        return GeminiTestResponse(
            success=False,
            message=f"Gemini AI bağlantı hatası: {error_msg}",
            model=settings.GEMINI_MODEL,
            details={
                "api_key_status": "✅ Tanımlı" if settings.GEMINI_API_KEY else "❌ Bulunamadı",
                "model_status": "❌ Erişilemedi",
                "error": error_msg,
                "test_status": "❌ Başarısız"
            }
        )


async def startup_gemini_test():
    """
    Backend başlangıcında otomatik çalışan Gemini test fonksiyonu
    """
    try:
        logger.info("\n" + "="*50)
        logger.info("🚀 GEMINI AI BAĞLANTI TESTİ BAŞLADI")
        logger.info("="*50)

        result = await test_gemini_connection()

        if result.success:
            logger.info("✅ " + "="*48)
            logger.info(f"✅ {result.message}")
            logger.info(f"✅ Model: {result.model}")
            logger.info("✅ " + "="*48 + "\n")
        else:
            logger.error("❌ " + "="*48)
            logger.error(f"❌ {result.message}")
            logger.error("❌ " + "="*48 + "\n")

    except Exception as e:
        logger.error("❌ " + "="*48)
        logger.error(f"❌ Gemini startup testi başarısız: {str(e)}")
        logger.error("❌ " + "="*48 + "\n")
