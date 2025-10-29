# -*- coding: utf-8 -*-
"""
Avatar Service for MarkaMind Platform
Handles avatar upload, processing, and management operations
"""

import os
import hashlib
import mimetypes
from typing import Optional, Dict, Any, Tuple
from io import BytesIO
from datetime import datetime, timezone
import logging

from PIL import Image, ImageOps
from fastapi import UploadFile, HTTPException
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)

class AvatarService:
    """Service for managing user avatars"""

    def __init__(self):
        # Supabase client initialization using settings
        if not settings.supabase_url or not settings.supabase_api_key:
            raise ValueError("Supabase credentials not found in environment variables")

        self.client: Client = create_client(settings.supabase_url, settings.supabase_api_key)
        self.bucket_name = settings.supabase_storage_bucket
        self.base_url = settings.avatar_base_url or f"{settings.supabase_url}/storage/v1/object/public/{self.bucket_name}/"

        # Configuration
        self.allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
        self.allowed_mime_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/webp'
        }
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.avatar_sizes = {
            'thumbnail': (64, 64),
            'small': (128, 128),
            'medium': (256, 256),
            'large': (512, 512)
        }

    async def upload_avatar(
        self,
        user_id: str,
        file: UploadFile
    ) -> Dict[str, Any]:
        """
        Upload and process user avatar

        Args:
            user_id: User UUID
            file: Uploaded image file

        Returns:
            Dict containing avatar information
        """
        try:
            # Validate file
            await self._validate_file(file)

            # Read file content
            file_content = await file.read()

            # Process image
            processed_images = await self._process_image(file_content)

            # Upload all sizes to storage
            upload_results = {}
            for size_name, image_data in processed_images.items():
                file_path = f"{user_id}/avatar_{size_name}.jpg"

                try:
                    # Upload to Supabase Storage using correct method
                    # First try to remove existing file if upsert
                    try:
                        self.client.storage.from_(self.bucket_name).remove([file_path])
                    except:
                        pass  # File might not exist, that's ok

                    # Upload new file
                    result = self.client.storage.from_(self.bucket_name).upload(
                        path=file_path,
                        file=image_data,
                        file_options={"content-type": "image/jpeg"}
                    )

                    # Log result for debugging
                    logger.debug(f"Upload result for {size_name}: {result}")

                    upload_results[size_name] = {
                        "path": file_path,
                        "url": f"{self.base_url}{file_path}",
                        "size": len(image_data)
                    }

                except Exception as e:
                    logger.error(f"Upload failed for {size_name}: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to upload {size_name} avatar"
                    )

            # Update user record in database
            await self._update_user_avatar(user_id, upload_results['large']['url'])

            return {
                "success": True,
                "avatar_url": upload_results['large']['url'],
                "avatar_type": "upload",
                "sizes": upload_results,
                "file_size": len(file_content),
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Avatar upload error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Avatar upload failed"
            )

    async def delete_avatar(self, user_id: str) -> Dict[str, Any]:
        """
        Delete user avatar from storage and database

        Args:
            user_id: User UUID

        Returns:
            Dict containing deletion result
        """
        try:
            # Delete all avatar sizes from storage
            deleted_files = []
            for size_name in self.avatar_sizes.keys():
                file_path = f"{user_id}/avatar_{size_name}.jpg"

                try:
                    result = self.client.storage.from_(self.bucket_name).remove([file_path])
                    deleted_files.append(file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")

            # Update user record - remove avatar
            await self._update_user_avatar(user_id, None, "gravatar")

            return {
                "success": True,
                "deleted_files": deleted_files,
                "message": "Avatar deleted successfully"
            }

        except Exception as e:
            logger.error(f"Avatar deletion error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Avatar deletion failed"
            )

    async def get_avatar_url(
        self,
        user_id: str,
        size: str = "large"
    ) -> Optional[str]:
        """
        Get avatar URL for user

        Args:
            user_id: User UUID
            size: Avatar size (thumbnail, small, medium, large)

        Returns:
            Avatar URL or None
        """
        try:
            if size not in self.avatar_sizes:
                size = "large"

            file_path = f"{user_id}/avatar_{size}.jpg"

            # Check if file exists in storage
            try:
                files = self.client.storage.from_(self.bucket_name).list(user_id)
                avatar_exists = any(
                    f.get('name') == f"avatar_{size}.jpg"
                    for f in files
                )

                if avatar_exists:
                    return f"{self.base_url}{file_path}"

            except Exception as e:
                logger.warning(f"Error checking avatar existence: {e}")

            return None

        except Exception as e:
            logger.error(f"Get avatar URL error: {e}")
            return None

    def generate_gravatar_url(self, email: str, size: int = 256) -> str:
        """
        Generate Gravatar URL from email

        Args:
            email: User email
            size: Avatar size

        Returns:
            Gravatar URL
        """
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=identicon"

    def generate_initials_avatar_url(self, full_name: str) -> str:
        """
        Generate initials avatar URL (placeholder)

        Args:
            full_name: User's full name

        Returns:
            Initials avatar URL
        """
        # For now, return a placeholder service URL
        # You can implement a proper initials generator service later
        initials = self._get_initials(full_name)
        return f"https://ui-avatars.com/api/?name={initials}&size=256&background=random"

    async def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB"
            )

        # Check MIME type
        if file.content_type not in self.allowed_mime_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(self.allowed_mime_types)}"
            )

        # Check file extension
        if file.filename:
            extension = file.filename.split('.')[-1].lower()
            if extension not in self.allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file extension. Allowed extensions: {', '.join(self.allowed_extensions)}"
                )

    async def _process_image(self, file_content: bytes) -> Dict[str, bytes]:
        """Process image into different sizes"""
        try:
            # Open image with PIL
            image = Image.open(BytesIO(file_content))

            # Convert to RGB if necessary (for JPEG)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background

            # Process each size
            processed_images = {}
            for size_name, (width, height) in self.avatar_sizes.items():
                # Resize image maintaining aspect ratio
                resized_image = ImageOps.fit(
                    image,
                    (width, height),
                    Image.Resampling.LANCZOS
                )

                # Save to bytes
                output = BytesIO()
                resized_image.save(
                    output,
                    format='JPEG',
                    quality=90,
                    optimize=True
                )
                processed_images[size_name] = output.getvalue()

            return processed_images

        except Exception as e:
            logger.error(f"Image processing error: {e}")
            raise HTTPException(
                status_code=400,
                detail="Invalid image file or processing failed"
            )

    async def _update_user_avatar(
        self,
        user_id: str,
        avatar_url: Optional[str],
        avatar_type: str = "upload"
    ) -> None:
        """Update user avatar in database"""
        try:
            update_data = {
                "avatar_url": avatar_url,
                "avatar_type": avatar_type,
                "avatar_updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

            result = self.client.table("users").update(update_data).eq("id", user_id).execute()

            if not result.data:
                logger.warning(f"No user found with ID: {user_id}")

        except Exception as e:
            logger.error(f"Database update error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update user avatar in database"
            )

    def _get_initials(self, full_name: str) -> str:
        """Extract initials from full name"""
        if not full_name:
            return "U"

        words = full_name.strip().split()
        if len(words) == 1:
            return words[0][0].upper()
        else:
            return f"{words[0][0]}{words[-1][0]}".upper()

# Create service instance
avatar_service = AvatarService()