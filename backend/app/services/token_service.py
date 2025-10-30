"""
Token Service
Email verification ve password reset token yönetimi
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
import hashlib
from app.config.supabase import supabase
from app.config import settings
from app.utils.password import generate_secure_token


class TokenService:
    """Token management service"""

    @staticmethod
    async def create_email_verification_token(user_id: str, email: str) -> str:
        """
        Email verification token oluştur

        Args:
            user_id: Kullanıcı ID
            email: Email adresi

        Returns:
            Plain text token (email'de gönderilecek)
        """
        try:
            # Random token oluştur
            plain_token = generate_secure_token(32)

            # Token'ı hash'le (database'e kaydedilecek)
            token_hash = hashlib.sha256(plain_token.encode()).hexdigest()

            # Expire süresi
            expires_at = datetime.utcnow() + timedelta(
                hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS
            )

            # Token'ı database'e kaydet
            token_data = {
                'user_id': user_id,
                'token_hash': token_hash,
                'email': email,
                'expires_at': expires_at.isoformat(),
                'created_at': datetime.utcnow().isoformat(),
                'used': False
            }

            result = supabase.table('email_verification_tokens').insert(token_data).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Token oluşturulamadı"
                )

            # Plain token'ı döndür (email'de gönderilecek)
            return plain_token

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token oluşturma hatası: {str(e)}"
            )

    @staticmethod
    async def verify_email_token(token: str) -> dict:
        """
        Email verification token'ı doğrula

        Args:
            token: Plain text token

        Returns:
            User bilgileri

        Raises:
            HTTPException: Token geçersiz veya süresi dolmuş
        """
        try:
            # Token'ı hash'le
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            # Token'ı database'den bul
            result = supabase.table('email_verification_tokens')\
                .select('*')\
                .eq('token_hash', token_hash)\
                .eq('used', False)\
                .execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Geçersiz veya kullanılmış token"
                )

            token_data = result.data[0]

            # Expire kontrolü
            expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
            if datetime.utcnow() > expires_at.replace(tzinfo=None):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token'ın süresi dolmuş"
                )

            # Kullanıcıyı email verified olarak işaretle
            user_update = supabase.table('users').update({
                'email_verified': True,
                'email_confirmed_at': datetime.utcnow().isoformat()
            }).eq('id', token_data['user_id']).execute()

            # Token'ı kullanılmış olarak işaretle
            supabase.table('email_verification_tokens').update({
                'used': True,
                'used_at': datetime.utcnow().isoformat()
            }).eq('id', token_data['id']).execute()

            return {
                "message": "Email başarıyla doğrulandı",
                "user_id": token_data['user_id']
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token doğrulama hatası: {str(e)}"
            )

    @staticmethod
    async def create_password_reset_token(user_id: str, email: str) -> str:
        """
        Password reset token oluştur

        Args:
            user_id: Kullanıcı ID
            email: Email adresi

        Returns:
            Plain text token
        """
        try:
            # Random token oluştur
            plain_token = generate_secure_token(32)

            # Token'ı hash'le
            token_hash = hashlib.sha256(plain_token.encode()).hexdigest()

            # Expire süresi (daha kısa - 1 saat)
            expires_at = datetime.utcnow() + timedelta(
                hours=settings.PASSWORD_RESET_EXPIRE_HOURS
            )

            # Token'ı database'e kaydet
            token_data = {
                'user_id': user_id,
                'token_hash': token_hash,
                'expires_at': expires_at.isoformat(),
                'created_at': datetime.utcnow().isoformat(),
                'used': False
            }

            result = supabase.table('password_reset_tokens').insert(token_data).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Token oluşturulamadı"
                )

            return plain_token

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token oluşturma hatası: {str(e)}"
            )

    @staticmethod
    async def verify_password_reset_token(token: str) -> dict:
        """
        Password reset token'ı doğrula

        Args:
            token: Plain text token

        Returns:
            Token data (user_id içerir)

        Raises:
            HTTPException: Token geçersiz veya süresi dolmuş
        """
        try:
            # Token'ı hash'le
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            # Token'ı database'den bul
            result = supabase.table('password_reset_tokens')\
                .select('*')\
                .eq('token_hash', token_hash)\
                .eq('used', False)\
                .execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Geçersiz veya kullanılmış token"
                )

            token_data = result.data[0]

            # Expire kontrolü
            expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
            if datetime.utcnow() > expires_at.replace(tzinfo=None):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token'ın süresi dolmuş"
                )

            return token_data

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token doğrulama hatası: {str(e)}"
            )

    @staticmethod
    async def mark_password_reset_token_used(token: str) -> bool:
        """
        Password reset token'ı kullanılmış olarak işaretle

        Args:
            token: Plain text token

        Returns:
            Success
        """
        try:
            # Token'ı hash'le
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            # Token'ı kullanılmış olarak işaretle
            result = supabase.table('password_reset_tokens').update({
                'used': True,
                'used_at': datetime.utcnow().isoformat()
            }).eq('token_hash', token_hash).execute()

            return True

        except Exception as e:
            return False

    @staticmethod
    async def cleanup_expired_tokens() -> dict:
        """
        Süresi dolmuş token'ları temizle

        Returns:
            Temizlenen token sayısı
        """
        try:
            now = datetime.utcnow().isoformat()

            # Email verification tokens
            email_result = supabase.table('email_verification_tokens')\
                .delete()\
                .lt('expires_at', now)\
                .execute()

            # Password reset tokens
            password_result = supabase.table('password_reset_tokens')\
                .delete()\
                .lt('expires_at', now)\
                .execute()

            return {
                "email_tokens_deleted": len(email_result.data) if email_result.data else 0,
                "password_tokens_deleted": len(password_result.data) if password_result.data else 0
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token temizleme hatası: {str(e)}"
            )

    @staticmethod
    async def resend_verification_email(email: str) -> dict:
        """
        Verification email'i tekrar gönder

        Args:
            email: Email adresi

        Returns:
            Success message
        """
        try:
            # Kullanıcıyı bul
            user_result = supabase.table('users').select('*').eq('email', email).execute()

            if not user_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Kullanıcı bulunamadı"
                )

            user = user_result.data[0]

            # Zaten doğrulanmış mı kontrol et
            if user.get('email_verified', False):
                return {
                    "message": "Email adresi zaten doğrulanmış"
                }

            # Yeni token oluştur
            token = await TokenService.create_email_verification_token(
                user_id=user['id'],
                email=email
            )

            # Email gönder (EmailService kullanacağız)
            from app.services.email_service import EmailService
            await EmailService.send_verification_email(
                email=email,
                full_name=user.get('full_name', ''),
                token=token
            )

            return {
                "message": "Doğrulama email'i tekrar gönderildi",
                "email": email
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Email gönderme hatası: {str(e)}"
            )
