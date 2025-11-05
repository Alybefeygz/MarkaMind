# -*- coding: utf-8 -*-
"""
Store Logo Service for MarkaMind Platform
Handles store logo upload, processing, and management operations
"""

import os
import mimetypes
from typing import Optional, Dict, Any
from io import BytesIO
from datetime import datetime, timezone
import logging

from PIL import Image, ImageOps
from fastapi import UploadFile, HTTPException
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)

class StoreLogoService:
    """Service for managing store logos"""

    def __init__(self):
        # Supabase client initialization
        if not settings.SUPABASE_URL or not settings.SUPABASE_API_KEY:
            raise ValueError("Supabase credentials not found")

        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_API_KEY
        )
        self.bucket_name = settings.STORE_LOGO_BUCKET
        self.base_url = settings.STORE_LOGO_BASE_URL or \
            f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket_name}/"

        # Configuration
        self.allowed_extensions = {'jpg', 'jpeg', 'png', 'svg', 'webp'}
        self.allowed_mime_types = {
            'image/jpeg', 'image/jpg', 'image/png',
            'image/svg+xml', 'image/webp'
        }
        self.max_file_size = 2 * 1024 * 1024  # 2MB (Logo'lar küçük olmalı)

        # Logo boyutları
        self.logo_sizes = {
            'thumbnail': (64, 64),      # Sidebar, listeler
            'small': (128, 128),        # Navbar
            'medium': (256, 256),       # Store detay sayfası
            'large': (512, 512)         # Büyük gösterimler
        }

    async def upload_logo(
        self,
        store_id: str,
        file: UploadFile
    ) -> Dict[str, Any]:
        """
        Upload and process store logo

        Args:
            store_id: Store UUID
            file: Uploaded logo file

        Returns:
            Dict containing logo information
        """
        try:
            # 1. Validate file
            await self._validate_file(file)

            # 2. Read file content
            file_content = await file.read()

            # 3. Process image (4 sizes)
            processed_images = await self._process_image(file_content)

            # 4. Upload all sizes to storage
            upload_results = {}
            for size_name, image_data in processed_images.items():
                file_path = f"{store_id}/logo_{size_name}.png"

                try:
                    # Remove existing file if exists
                    try:
                        self.client.storage.from_(self.bucket_name).remove([file_path])
                    except Exception as e:
                        logger.debug(f"Could not remove existing file {file_path}: {e}")

                    # Upload new file
                    result = self.client.storage.from_(self.bucket_name).upload(
                        path=file_path,
                        file=image_data,
                        file_options={"content-type": "image/png"}
                    )

                    upload_results[size_name] = {
                        "path": file_path,
                        "url": f"{self.base_url}{file_path}",
                        "size": len(image_data)
                    }

                except Exception as e:
                    logger.error(f"Upload failed for {size_name}: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to upload {size_name} logo"
                    )

            # 5. Update store record in database
            await self._update_store_logo(store_id, upload_results['large']['url'])

            return {
                "success": True,
                "logo_url": upload_results['large']['url'],
                "sizes": upload_results,
                "file_size": len(file_content),
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Logo upload error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Logo upload failed"
            )

    async def delete_logo(self, store_id: str) -> Dict[str, Any]:
        """
        Delete store logo from storage and database

        Args:
            store_id: Store UUID

        Returns:
            Dict containing deletion result
        """
        try:
            # Delete all logo sizes from storage
            deleted_files = []
            for size_name in self.logo_sizes.keys():
                file_path = f"{store_id}/logo_{size_name}.png"

                try:
                    result = self.client.storage.from_(self.bucket_name).remove([file_path])
                    deleted_files.append(file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")

            # Update store record - remove logo
            await self._update_store_logo(store_id, None)

            return {
                "success": True,
                "deleted_files": deleted_files,
                "message": "Logo deleted successfully"
            }

        except Exception as e:
            logger.error(f"Logo deletion error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Logo deletion failed"
            )

    async def get_logo_url(
        self,
        store_id: str,
        size: str = "large"
    ) -> Optional[str]:
        """
        Get logo URL for store

        Args:
            store_id: Store UUID
            size: Logo size (thumbnail, small, medium, large)

        Returns:
            Logo URL or None
        """
        try:
            if size not in self.logo_sizes:
                size = "large"

            file_path = f"{store_id}/logo_{size}.png"

            # Check if file exists in storage
            try:
                files = self.client.storage.from_(self.bucket_name).list(store_id)
                logo_exists = any(
                    f.get('name') == f"logo_{size}.png"
                    for f in files
                )

                if logo_exists:
                    return f"{self.base_url}{file_path}"

            except Exception as e:
                logger.warning(f"Error checking logo existence: {e}")

            return None

        except Exception as e:
            logger.error(f"Get logo URL error: {e}")
            return None

    async def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        # Check file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

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
                    detail=f"Invalid file extension. Allowed: {', '.join(self.allowed_extensions)}"
                )

    async def _process_image(self, file_content: bytes) -> Dict[str, bytes]:
        """Process image into different sizes"""
        try:
            # Open image with PIL
            image = Image.open(BytesIO(file_content))

            # Preserve transparency for PNG
            # Convert to RGBA if not already
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            # Process each size
            processed_images = {}
            for size_name, (width, height) in self.logo_sizes.items():
                # Resize image maintaining aspect ratio
                resized_image = ImageOps.fit(
                    image,
                    (width, height),
                    Image.Resampling.LANCZOS
                )

                # Save to bytes as PNG
                output = BytesIO()
                resized_image.save(
                    output,
                    format='PNG',
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

    async def _update_store_logo(
        self,
        store_id: str,
        logo_url: Optional[str]
    ) -> None:
        """Update store logo in database"""
        try:
            update_data = {
                "logo": logo_url,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

            result = self.client.table("stores").update(update_data).eq("id", store_id).execute()

            if not result.data:
                logger.warning(f"No store found with ID: {store_id}")

        except Exception as e:
            logger.error(f"Database update error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update store logo in database"
            )

# Create service instance
store_logo_service = StoreLogoService()
