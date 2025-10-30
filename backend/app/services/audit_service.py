"""
Audit Service
Güvenlik ve kullanıcı aktivitelerini loglama
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from app.config.supabase import supabase
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """Audit logging service"""

    @staticmethod
    async def log_event(
        user_id: str,
        event_type: str,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Güvenlik/aktivite event'i logla

        Args:
            user_id: Kullanıcı ID
            event_type: Event tipi (login_success, login_failed, password_changed, vb.)
            description: Event açıklaması
            ip_address: İstek IP adresi
            user_agent: User agent string
            metadata: Ek bilgiler (JSON)

        Returns:
            Log entry
        """
        try:
            # Log entry oluştur
            log_data = {
                'user_id': user_id,
                'event_type': event_type,
                'description': description,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'metadata': metadata,
                'created_at': datetime.utcnow().isoformat()
            }

            # Database'e kaydet
            result = supabase.table('user_audit_log').insert(log_data).execute()

            if not result.data:
                logger.error(f"Failed to create audit log for user {user_id}")
                return {}

            logger.info(f"Audit log created: {event_type} for user {user_id}")
            return result.data[0]

        except Exception as e:
            logger.error(f"Audit logging error: {str(e)}")
            # Audit logging hatası uygulama akışını bozmamalı
            return {}

    @staticmethod
    async def get_user_audit_logs(
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Kullanıcının audit loglarını getir

        Args:
            user_id: Kullanıcı ID
            limit: Maksimum kayıt sayısı
            offset: Offset
            event_type: Event tipi filtresi (opsiyonel)

        Returns:
            Audit log listesi
        """
        try:
            query = supabase.table('user_audit_log')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)

            # Event type filtresi varsa ekle
            if event_type:
                query = query.eq('event_type', event_type)

            result = query.execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Get audit logs error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Audit logları getirilemedi"
            )

    @staticmethod
    async def get_recent_logins(
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Kullanıcının son giriş loglarını getir

        Args:
            user_id: Kullanıcı ID
            limit: Maksimum kayıt sayısı

        Returns:
            Login log listesi
        """
        try:
            result = supabase.table('user_audit_log')\
                .select('*')\
                .eq('user_id', user_id)\
                .in_('event_type', ['login_success', 'login_failed'])\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Get recent logins error: {str(e)}")
            return []

    @staticmethod
    async def get_failed_login_attempts(
        user_id: str,
        minutes: int = 15
    ) -> int:
        """
        Belirli süre içindeki başarısız giriş denemelerini say

        Args:
            user_id: Kullanıcı ID
            minutes: Kaç dakika geriye bakılacak

        Returns:
            Başarısız giriş sayısı
        """
        try:
            from datetime import timedelta

            # X dakika önceki zaman
            time_threshold = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat()

            result = supabase.table('user_audit_log')\
                .select('id')\
                .eq('user_id', user_id)\
                .eq('event_type', 'login_failed')\
                .gte('created_at', time_threshold)\
                .execute()

            return len(result.data) if result.data else 0

        except Exception as e:
            logger.error(f"Get failed login attempts error: {str(e)}")
            return 0

    @staticmethod
    async def check_rate_limit(
        user_id: str,
        event_type: str,
        max_attempts: int,
        window_minutes: int
    ) -> tuple[bool, int]:
        """
        Rate limit kontrolü

        Args:
            user_id: Kullanıcı ID
            event_type: Event tipi
            max_attempts: Maksimum deneme sayısı
            window_minutes: Zaman penceresi (dakika)

        Returns:
            (is_allowed, remaining_attempts) tuple
        """
        try:
            from datetime import timedelta

            # Zaman penceresi
            time_threshold = (datetime.utcnow() - timedelta(minutes=window_minutes)).isoformat()

            # Bu zaman dilimindeki deneme sayısı
            result = supabase.table('user_audit_log')\
                .select('id')\
                .eq('user_id', user_id)\
                .eq('event_type', event_type)\
                .gte('created_at', time_threshold)\
                .execute()

            attempt_count = len(result.data) if result.data else 0
            remaining = max_attempts - attempt_count

            is_allowed = attempt_count < max_attempts

            return is_allowed, max(0, remaining)

        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            # Hata durumunda izin ver
            return True, max_attempts

    @staticmethod
    async def get_user_statistics(user_id: str) -> Dict[str, Any]:
        """
        Kullanıcı istatistiklerini getir

        Args:
            user_id: Kullanıcı ID

        Returns:
            İstatistikler dictionary
        """
        try:
            # Toplam login sayısı
            login_result = supabase.table('user_audit_log')\
                .select('id')\
                .eq('user_id', user_id)\
                .eq('event_type', 'login_success')\
                .execute()

            total_logins = len(login_result.data) if login_result.data else 0

            # Son login
            last_login_result = supabase.table('user_audit_log')\
                .select('created_at')\
                .eq('user_id', user_id)\
                .eq('event_type', 'login_success')\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()

            last_login = None
            if last_login_result.data:
                last_login = last_login_result.data[0]['created_at']

            # Şifre sıfırlama sayısı
            password_reset_result = supabase.table('user_audit_log')\
                .select('id')\
                .eq('user_id', user_id)\
                .eq('event_type', 'password_reset')\
                .execute()

            total_password_resets = len(password_reset_result.data) if password_reset_result.data else 0

            # Toplam event sayısı
            total_events_result = supabase.table('user_audit_log')\
                .select('id')\
                .eq('user_id', user_id)\
                .execute()

            total_events = len(total_events_result.data) if total_events_result.data else 0

            # Kullanıcı oluşturulma tarihi
            user_result = supabase.table('users')\
                .select('created_at, email_verified')\
                .eq('id', user_id)\
                .execute()

            account_age_days = 0
            is_verified = False

            if user_result.data:
                user_data = user_result.data[0]
                created_at = datetime.fromisoformat(user_data['created_at'].replace('Z', '+00:00'))
                account_age_days = (datetime.utcnow() - created_at.replace(tzinfo=None)).days
                is_verified = user_data.get('email_verified', False)

            return {
                "total_logins": total_logins,
                "last_login": last_login,
                "total_password_resets": total_password_resets,
                "account_age_days": account_age_days,
                "is_verified": is_verified,
                "total_audit_events": total_events
            }

        except Exception as e:
            logger.error(f"Get user statistics error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="İstatistikler getirilemedi"
            )

    @staticmethod
    async def cleanup_old_logs(days: int = 90) -> int:
        """
        Eski audit logları temizle

        Args:
            days: Kaç gün öncesine kadar saklanacak

        Returns:
            Silinen kayıt sayısı
        """
        try:
            from datetime import timedelta

            # Threshold date
            threshold_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            # Eski logları sil
            result = supabase.table('user_audit_log')\
                .delete()\
                .lt('created_at', threshold_date)\
                .execute()

            deleted_count = len(result.data) if result.data else 0

            logger.info(f"Cleaned up {deleted_count} old audit logs")
            return deleted_count

        except Exception as e:
            logger.error(f"Cleanup old logs error: {str(e)}")
            return 0
