"""
User Service
Kullanıcı CRUD ve profil yönetimi
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from app.config.supabase import supabase
from app.utils.password import hash_password, verify_password
from app.schemas.user import UserResponse, UserUpdate, UserProfile, UserStats
from app.services.audit_service import AuditService
import logging

logger = logging.getLogger(__name__)


class UserService:
    """User management service"""

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[UserResponse]:
        """
        Kullanıcıyı ID ile getir

        Args:
            user_id: Kullanıcı ID

        Returns:
            UserResponse veya None
        """
        try:
            result = supabase.table('users').select('*').eq('id', user_id).execute()

            if not result.data:
                return None

            user = result.data[0]

            return UserResponse(
                id=user['id'],
                email=user['email'],
                username=user.get('username'),
                full_name=user.get('full_name'),
                role=user.get('role', 'user'),
                email_verified=user.get('email_verified', False),
                avatar_url=user.get('avatar_url'),
                created_at=user['created_at'],
                last_login=user.get('last_login')
            )

        except Exception as e:
            logger.error(f"Get user by ID error: {str(e)}")
            return None

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[UserResponse]:
        """
        Kullanıcıyı email ile getir

        Args:
            email: Email adresi

        Returns:
            UserResponse veya None
        """
        try:
            result = supabase.table('users').select('*').eq('email', email).execute()

            if not result.data:
                return None

            user = result.data[0]

            return UserResponse(
                id=user['id'],
                email=user['email'],
                username=user.get('username'),
                full_name=user.get('full_name'),
                role=user.get('role', 'user'),
                email_verified=user.get('email_verified', False),
                avatar_url=user.get('avatar_url'),
                created_at=user['created_at'],
                last_login=user.get('last_login')
            )

        except Exception as e:
            logger.error(f"Get user by email error: {str(e)}")
            return None

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[UserResponse]:
        """
        Kullanıcıyı username ile getir

        Args:
            username: Kullanıcı adı

        Returns:
            UserResponse veya None
        """
        try:
            result = supabase.table('users').select('*').eq('username', username.lower()).execute()

            if not result.data:
                return None

            user = result.data[0]

            return UserResponse(
                id=user['id'],
                email=user['email'],
                username=user.get('username'),
                full_name=user.get('full_name'),
                role=user.get('role', 'user'),
                email_verified=user.get('email_verified', False),
                avatar_url=user.get('avatar_url'),
                created_at=user['created_at'],
                last_login=user.get('last_login')
            )

        except Exception as e:
            logger.error(f"Get user by username error: {str(e)}")
            return None

    @staticmethod
    async def update_user(user_id: str, update_data: UserUpdate) -> UserResponse:
        """
        Kullanıcı bilgilerini güncelle

        Args:
            user_id: Kullanıcı ID
            update_data: Güncellenecek veriler

        Returns:
            Güncellenmiş UserResponse

        Raises:
            HTTPException: Güncelleme başarısız
        """
        try:
            # Sadece değişen alanları al
            update_dict = update_data.model_dump(exclude_unset=True)

            if not update_dict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Güncellenecek alan bulunamadı"
                )

            # Username varsa lowercase yap
            if 'username' in update_dict:
                update_dict['username'] = update_dict['username'].lower()

                # Username benzersizliği kontrolü
                existing = supabase.table('users')\
                    .select('id')\
                    .eq('username', update_dict['username'])\
                    .neq('id', user_id)\
                    .execute()

                if existing.data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Bu kullanıcı adı zaten kullanımda"
                    )

            # Updated_at ekle
            update_dict['updated_at'] = datetime.utcnow().isoformat()

            # Güncelle
            result = supabase.table('users')\
                .update(update_dict)\
                .eq('id', user_id)\
                .execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Kullanıcı bulunamadı"
                )

            user = result.data[0]

            # Audit log
            await AuditService.log_event(
                user_id=user_id,
                event_type='profile_updated',
                description=f'Profil güncellendi: {", ".join(update_dict.keys())}'
            )

            return UserResponse(
                id=user['id'],
                email=user['email'],
                username=user.get('username'),
                full_name=user.get('full_name'),
                role=user.get('role', 'user'),
                email_verified=user.get('email_verified', False),
                avatar_url=user.get('avatar_url'),
                created_at=user['created_at'],
                last_login=user.get('last_login')
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Update user error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Kullanıcı güncellenemedi: {str(e)}"
            )

    @staticmethod
    async def change_password(
        user_id: str,
        old_password: str,
        new_password: str
    ) -> dict:
        """
        Kullanıcı şifresini değiştir

        Args:
            user_id: Kullanıcı ID
            old_password: Mevcut şifre
            new_password: Yeni şifre

        Returns:
            Success message

        Raises:
            HTTPException: Şifre değiştirme başarısız
        """
        try:
            # Kullanıcıyı getir
            result = supabase.table('users').select('*').eq('id', user_id).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Kullanıcı bulunamadı"
                )

            user = result.data[0]

            # Mevcut şifreyi kontrol et
            if not verify_password(old_password, user['password_hash']):
                # Failed attempt audit log
                await AuditService.log_event(
                    user_id=user_id,
                    event_type='password_change_failed',
                    description='Hatalı mevcut şifre'
                )

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Mevcut şifre hatalı"
                )

            # Yeni şifreyi hash'le
            new_password_hash = hash_password(new_password)

            # Şifreyi güncelle
            supabase.table('users').update({
                'password_hash': new_password_hash,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user_id).execute()

            # Audit log
            await AuditService.log_event(
                user_id=user_id,
                event_type='password_changed',
                description='Şifre değiştirildi'
            )

            return {"message": "Şifre başarıyla değiştirildi"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Change password error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Şifre değiştirilemedi: {str(e)}"
            )

    @staticmethod
    async def reset_password(user_id: str, new_password: str) -> dict:
        """
        Şifre sıfırlama (token ile)

        Args:
            user_id: Kullanıcı ID
            new_password: Yeni şifre

        Returns:
            Success message
        """
        try:
            # Yeni şifreyi hash'le
            new_password_hash = hash_password(new_password)

            # Şifreyi güncelle
            result = supabase.table('users').update({
                'password_hash': new_password_hash,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user_id).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Kullanıcı bulunamadı"
                )

            # Audit log
            await AuditService.log_event(
                user_id=user_id,
                event_type='password_reset',
                description='Şifre sıfırlandı'
            )

            return {"message": "Şifre başarıyla sıfırlandı"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Reset password error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Şifre sıfırlanamadı: {str(e)}"
            )

    @staticmethod
    async def get_user_profile(user_id: str) -> UserProfile:
        """
        Kullanıcı profili getir (public)

        Args:
            user_id: Kullanıcı ID

        Returns:
            UserProfile

        Raises:
            HTTPException: Kullanıcı bulunamadı
        """
        try:
            result = supabase.table('users').select('*').eq('id', user_id).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Kullanıcı bulunamadı"
                )

            user = result.data[0]

            return UserProfile(
                id=user['id'],
                email=user['email'],
                username=user.get('username'),
                full_name=user.get('full_name'),
                role=user.get('role', 'user'),
                email_verified=user.get('email_verified', False),
                avatar_url=user.get('avatar_url'),
                created_at=user['created_at']
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get user profile error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Profil getirilemedi"
            )

    @staticmethod
    async def get_user_stats(user_id: str) -> UserStats:
        """
        Kullanıcı istatistikleri getir

        Args:
            user_id: Kullanıcı ID

        Returns:
            UserStats

        Raises:
            HTTPException: İstatistikler getirilemedi
        """
        try:
            stats = await AuditService.get_user_statistics(user_id)

            return UserStats(
                total_logins=stats['total_logins'],
                last_login_date=stats['last_login'],
                total_password_resets=stats['total_password_resets'],
                account_age_days=stats['account_age_days'],
                is_verified=stats['is_verified'],
                total_audit_events=stats['total_audit_events']
            )

        except Exception as e:
            logger.error(f"Get user stats error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="İstatistikler getirilemedi"
            )

    @staticmethod
    async def delete_user(user_id: str) -> dict:
        """
        Kullanıcıyı sil (soft delete - is_active = false)

        Args:
            user_id: Kullanıcı ID

        Returns:
            Success message
        """
        try:
            result = supabase.table('users').update({
                'is_active': False,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user_id).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Kullanıcı bulunamadı"
                )

            # Audit log
            await AuditService.log_event(
                user_id=user_id,
                event_type='account_deactivated',
                description='Hesap devre dışı bırakıldı'
            )

            return {"message": "Hesap devre dışı bırakıldı"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Delete user error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Hesap silinemedi"
            )

    @staticmethod
    async def activate_user(user_id: str) -> dict:
        """
        Kullanıcıyı aktif et

        Args:
            user_id: Kullanıcı ID

        Returns:
            Success message
        """
        try:
            result = supabase.table('users').update({
                'is_active': True,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user_id).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Kullanıcı bulunamadı"
                )

            # Audit log
            await AuditService.log_event(
                user_id=user_id,
                event_type='account_activated',
                description='Hesap aktif edildi'
            )

            return {"message": "Hesap aktif edildi"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Activate user error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Hesap aktif edilemedi"
            )

    @staticmethod
    async def upload_avatar(
        user_id: str,
        file,
        file_content: bytes
    ) -> Optional[str]:
        """
        Upload user avatar to Supabase Storage

        Args:
            user_id: Kullanıcı ID
            file: Upload file object
            file_content: File byte content

        Returns:
            Avatar URL or None

        Raises:
            HTTPException: Upload failed
        """
        try:
            import uuid
            import os

            bucket_name = "user-avatars"

            # Generate unique filename
            file_ext = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{user_id}/{uuid.uuid4()}{file_ext}"

            # Get current avatar to delete old one
            current_avatar = await UserService.get_avatar_data(user_id)

            # Determine correct MIME type from file extension
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            content_type = mime_types.get(file_ext, 'image/jpeg')

            logger.info(f"File extension: {file_ext}, Content-Type: {content_type}")

            # Upload to Supabase Storage
            upload_result = supabase.storage.from_(bucket_name).upload(
                path=unique_filename,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "cache-control": "3600",
                    "upsert": "false"
                }
            )

            # Get public URL
            public_url = supabase.storage.from_(bucket_name).get_public_url(unique_filename)

            # Clean URL: Remove trailing ? character
            clean_url = public_url.rstrip('?') if public_url else public_url

            logger.info(f"Original URL: {public_url}")
            logger.info(f"Cleaned URL: {clean_url}")

            # Update user record in database
            update_data = {
                "avatar_url": clean_url,
                "avatar_type": "upload",
                "avatar_updated_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            supabase.table('users').update(update_data).eq('id', user_id).execute()

            # Delete old avatar if exists and is uploaded type
            if current_avatar.get("avatar_type") == "upload" and current_avatar.get("avatar_url"):
                await UserService._delete_avatar_file(current_avatar.get("avatar_url"), bucket_name)

            # Audit log
            await AuditService.log_event(
                user_id=user_id,
                event_type='avatar_uploaded',
                description='Profil fotoğrafı yüklendi'
            )

            logger.info(f"Avatar uploaded successfully for user: {user_id}")
            return clean_url

        except Exception as e:
            logger.error(f"Avatar upload error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Avatar yüklenemedi: {str(e)}"
            )

    @staticmethod
    async def delete_avatar(user_id: str) -> bool:
        """
        Delete user avatar

        Args:
            user_id: Kullanıcı ID

        Returns:
            True if successful

        Raises:
            HTTPException: Delete failed
        """
        try:
            bucket_name = "user-avatars"

            # Get current avatar
            avatar_data = await UserService.get_avatar_data(user_id)

            # Update user record to remove avatar
            update_data = {
                "avatar_url": None,
                "avatar_type": "gravatar",
                "avatar_updated_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            supabase.table('users').update(update_data).eq('id', user_id).execute()

            # Delete file from storage if it was uploaded
            if avatar_data.get("avatar_type") == "upload" and avatar_data.get("avatar_url"):
                await UserService._delete_avatar_file(avatar_data.get("avatar_url"), bucket_name)

            # Audit log
            await AuditService.log_event(
                user_id=user_id,
                event_type='avatar_deleted',
                description='Profil fotoğrafı silindi'
            )

            logger.info(f"Avatar deleted for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Avatar delete error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Avatar silinemedi: {str(e)}"
            )

    @staticmethod
    async def get_avatar_data(user_id: str) -> Dict[str, Any]:
        """
        Get user avatar URL and metadata

        Args:
            user_id: Kullanıcı ID

        Returns:
            Avatar data dictionary
        """
        try:
            result = supabase.table('users')\
                .select('avatar_url, avatar_type, avatar_updated_at')\
                .eq('id', user_id)\
                .execute()

            if result.data and len(result.data) > 0:
                return result.data[0]

            return {
                "avatar_url": None,
                "avatar_type": "gravatar",
                "avatar_updated_at": None
            }

        except Exception as e:
            logger.error(f"Get avatar data error: {e}")
            return {
                "avatar_url": None,
                "avatar_type": "gravatar",
                "avatar_updated_at": None
            }

    @staticmethod
    async def _delete_avatar_file(avatar_url: str, bucket_name: str) -> bool:
        """
        Delete avatar file from Supabase Storage

        Args:
            avatar_url: Avatar URL
            bucket_name: Storage bucket name

        Returns:
            True if successful
        """
        try:
            # Extract file path from URL
            # URL format: https://{project}.supabase.co/storage/v1/object/public/user-avatars/{path}
            if bucket_name in avatar_url:
                # Get the path after bucket name
                path_start = avatar_url.find(bucket_name) + len(bucket_name) + 1
                file_path = avatar_url[path_start:]

                # Delete from storage
                supabase.storage.from_(bucket_name).remove([file_path])

                logger.info(f"Old avatar file deleted: {file_path}")
                return True

        except Exception as e:
            logger.error(f"Delete avatar file error: {e}")
            return False

        return False
