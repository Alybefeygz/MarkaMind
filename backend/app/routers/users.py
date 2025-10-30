# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional
from app.dependencies import get_current_user
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/avatar/upload")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload or update user avatar
    """
    try:
        user_id = current_user.get("id")

        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sadece resim dosyaları yüklenebilir (JPEG, PNG, GIF, WebP)"
            )

        # Validate file size (max 5MB)
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dosya boyutu 5MB'dan küçük olmalıdır"
            )

        # Reset file pointer
        await file.seek(0)

        # Upload avatar
        avatar_url = await UserService.upload_avatar(
            user_id=user_id,
            file=file,
            file_content=file_content
        )

        if not avatar_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Avatar yüklenemedi"
            )

        logger.info(f"Avatar uploaded for user: {user_id}")

        return {
            "message": "Avatar başarıyla yüklendi",
            "avatar_url": avatar_url,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Avatar upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Avatar yüklenirken bir hata oluştu"
        )


@router.delete("/avatar")
async def delete_avatar(
    current_user: dict = Depends(get_current_user)
):
    """
    Delete user avatar
    """
    try:
        user_id = current_user.get("id")

        # Delete avatar
        success = await UserService.delete_avatar(user_id=user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Avatar silinemedi"
            )

        logger.info(f"Avatar deleted for user: {user_id}")

        return {
            "message": "Avatar başarıyla silindi",
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Avatar delete failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Avatar silinirken bir hata oluştu"
        )


@router.get("/avatar")
async def get_avatar_url(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user avatar URL
    """
    try:
        user_id = current_user.get("id")

        # Get avatar URL from database
        avatar_data = await UserService.get_avatar_data(user_id=user_id)

        return {
            "avatar_url": avatar_data.get("avatar_url"),
            "avatar_type": avatar_data.get("avatar_type", "gravatar"),
            "avatar_updated_at": avatar_data.get("avatar_updated_at")
        }

    except Exception as e:
        logger.error(f"Get avatar URL failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Avatar bilgisi alınamadı"
        )


@router.post("/avatar/refresh-metadata")
async def refresh_avatar_metadata(
    current_user: dict = Depends(get_current_user)
):
    """
    Refresh avatar metadata (force re-check MIME type)
    Useful for fixing old uploads with wrong content-type
    """
    try:
        user_id = current_user.get("id")

        # Get current avatar
        avatar_data = await UserService.get_avatar_data(user_id=user_id)

        if not avatar_data.get("avatar_url") or avatar_data.get("avatar_type") != "upload":
            return {
                "message": "No uploaded avatar to refresh",
                "success": False
            }

        # Return info - user should re-upload the avatar
        return {
            "message": "Lütfen profil fotoğrafınızı yeniden yükleyin (MIME type düzeltilmesi için)",
            "avatar_url": avatar_data.get("avatar_url"),
            "suggestion": "Eski avatar silinip yeniden yüklenmelidir",
            "success": True
        }

    except Exception as e:
        logger.error(f"Refresh avatar metadata failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Avatar metadata güncellenemedi"
        )
