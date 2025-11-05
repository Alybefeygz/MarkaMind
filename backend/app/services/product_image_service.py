# -*- coding: utf-8 -*-
"""
Product Image Service for MarkaMind Platform
Handles product image upload, processing, and management operations
Supports multiple images per product with ordering
"""

import os
import mimetypes
from typing import Optional, Dict, Any, List
from io import BytesIO
from datetime import datetime, timezone
import logging

from PIL import Image, ImageOps
from fastapi import UploadFile, HTTPException
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)

class ProductImageService:
    """Service for managing product images"""

    def __init__(self):
        # Supabase client initialization
        if not settings.SUPABASE_URL or not settings.SUPABASE_API_KEY:
            raise ValueError("Supabase credentials not found")

        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_API_KEY
        )
        self.bucket_name = settings.PRODUCT_IMAGE_BUCKET
        self.base_url = settings.PRODUCT_IMAGE_BASE_URL or \
            f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket_name}/"

        # Configuration
        self.allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
        self.allowed_mime_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/webp'
        }
        self.max_file_size = 10 * 1024 * 1024  # 10MB (Ürün resimleri daha büyük)
        self.max_images_per_product = 10  # Max 10 resim per ürün

        # Image boyutları (E-commerce için optimize)
        self.image_sizes = {
            'thumbnail': (64, 64),      # Liste/grid görünümü
            'small': (200, 200),        # Kart görünümü
            'medium': (500, 500),       # Detay sayfası ana resim
            'large': (1000, 1000)       # Zoom/büyütme özelliği
        }

    async def upload_image(
        self,
        product_id: str,
        file: UploadFile,
        display_order: int = 0,
        is_primary: bool = False
    ) -> Dict[str, Any]:
        """
        Upload single product image

        Args:
            product_id: Product UUID
            file: Uploaded image file
            display_order: Image order (0-based)
            is_primary: Mark as primary/main image

        Returns:
            Dict containing image information with image_id
        """
        try:
            # 1. Check image count limit
            current_count = await self._get_image_count(product_id)
            if current_count >= self.max_images_per_product:
                raise HTTPException(
                    status_code=400,
                    detail=f"Maximum {self.max_images_per_product} images allowed per product"
                )

            # 2. Validate file
            await self._validate_file(file)

            # 3. Read file content
            file_content = await file.read()

            # 4. Get next image index
            next_index = current_count + 1

            # 5. Process image (4 sizes)
            processed_images = await self._process_image(file_content)

            # 6. Upload all sizes to storage
            upload_results = {}
            for size_name, image_data in processed_images.items():
                file_path = f"{product_id}/image_{next_index}_{size_name}.jpg"

                try:
                    # Remove existing file if exists (upsert)
                    try:
                        self.client.storage.from_(self.bucket_name).remove([file_path])
                    except:
                        pass

                    # Upload new file
                    result = self.client.storage.from_(self.bucket_name).upload(
                        path=file_path,
                        file=image_data,
                        file_options={"content-type": "image/jpeg"}
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
                        detail=f"Failed to upload {size_name} image"
                    )

            # 7. Create image record in database
            image_id = await self._create_image_record(
                product_id=product_id,
                image_url=upload_results['large']['url'],
                thumbnail_url=upload_results['thumbnail']['url'],
                display_order=display_order,
                is_primary=is_primary
            )

            # 8. If primary, update other images
            if is_primary:
                await self._unset_other_primary_images(product_id, image_id)

            return {
                "success": True,
                "image_id": image_id,
                "image_url": upload_results['large']['url'],
                "thumbnail_url": upload_results['thumbnail']['url'],
                "sizes": upload_results,
                "display_order": display_order,
                "is_primary": is_primary,
                "file_size": len(file_content),
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Product image upload error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Product image upload failed"
            )

    async def upload_multiple_images(
        self,
        product_id: str,
        files: List[UploadFile]
    ) -> List[Dict[str, Any]]:
        """
        Upload multiple product images at once

        Args:
            product_id: Product UUID
            files: List of uploaded image files

        Returns:
            List of upload results
        """
        try:
            # Check total count
            current_count = await self._get_image_count(product_id)
            if current_count + len(files) > self.max_images_per_product:
                raise HTTPException(
                    status_code=400,
                    detail=f"Would exceed maximum {self.max_images_per_product} images per product"
                )

            results = []
            for index, file in enumerate(files):
                # First image is primary if no images exist
                is_primary = (current_count == 0 and index == 0)
                display_order = current_count + index

                result = await self.upload_image(
                    product_id=product_id,
                    file=file,
                    display_order=display_order,
                    is_primary=is_primary
                )
                results.append(result)

            return results

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Multiple image upload error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Multiple image upload failed"
            )

    async def delete_image(self, image_id: str) -> Dict[str, Any]:
        """
        Delete single product image

        Args:
            image_id: Image record UUID

        Returns:
            Deletion result
        """
        try:
            # 1. Get image record
            image_record = await self._get_image_record(image_id)
            if not image_record:
                raise HTTPException(
                    status_code=404,
                    detail="Image not found"
                )

            product_id = image_record['product_id']

            # 2. Extract image index from URL
            # URL format: .../product_id/image_1_large.jpg
            image_url = image_record['image_url']
            image_index = self._extract_image_index(image_url)

            # 3. Delete all sizes from storage
            deleted_files = []
            for size_name in self.image_sizes.keys():
                file_path = f"{product_id}/image_{image_index}_{size_name}.jpg"

                try:
                    self.client.storage.from_(self.bucket_name).remove([file_path])
                    deleted_files.append(file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")

            # 4. Delete database record
            await self._delete_image_record(image_id)

            # 5. If was primary, set another image as primary
            if image_record.get('is_primary'):
                await self._set_first_image_as_primary(product_id)

            return {
                "success": True,
                "deleted_files": deleted_files,
                "message": "Image deleted successfully"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Image deletion error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Image deletion failed"
            )

    async def delete_all_images(self, product_id: str) -> Dict[str, Any]:
        """
        Delete all images for a product

        Args:
            product_id: Product UUID

        Returns:
            Deletion result
        """
        try:
            # Get all image records
            images = await self._get_all_images(product_id)

            deleted_count = 0
            for image in images:
                try:
                    await self.delete_image(image['id'])
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete image {image['id']}: {e}")

            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Deleted {deleted_count} images"
            }

        except Exception as e:
            logger.error(f"Delete all images error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to delete all images"
            )

    async def set_primary_image(self, image_id: str) -> Dict[str, Any]:
        """
        Set an image as primary/main image

        Args:
            image_id: Image record UUID

        Returns:
            Update result
        """
        try:
            # Get image record
            image_record = await self._get_image_record(image_id)
            if not image_record:
                raise HTTPException(
                    status_code=404,
                    detail="Image not found"
                )

            product_id = image_record['product_id']

            # Unset all other primary images
            await self._unset_other_primary_images(product_id, image_id)

            # Set this as primary
            await self._update_image_primary(image_id, True)

            return {
                "success": True,
                "message": "Primary image updated"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Set primary image error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to set primary image"
            )

    async def reorder_images(
        self,
        product_id: str,
        order_list: List[Dict[str, int]]
    ) -> Dict[str, Any]:
        """
        Reorder product images

        Args:
            product_id: Product UUID
            order_list: List of {"image_id": "...", "display_order": 0}

        Returns:
            Update result
        """
        try:
            for item in order_list:
                image_id = item['image_id']
                display_order = item['display_order']

                await self._update_image_order(image_id, display_order)

            return {
                "success": True,
                "message": f"Reordered {len(order_list)} images"
            }

        except Exception as e:
            logger.error(f"Reorder images error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to reorder images"
            )

    async def get_image_url(
        self,
        image_id: str,
        size: str = "large"
    ) -> Optional[str]:
        """
        Get image URL for specific size

        Args:
            image_id: Image record UUID
            size: Image size

        Returns:
            Image URL
        """
        try:
            if size not in self.image_sizes:
                size = "large"

            # Get image record
            image_record = await self._get_image_record(image_id)
            if not image_record:
                return None

            # Extract index and build URL
            image_url = image_record['image_url']
            image_index = self._extract_image_index(image_url)
            product_id = image_record['product_id']

            file_path = f"{product_id}/image_{image_index}_{size}.jpg"
            return f"{self.base_url}{file_path}"

        except Exception as e:
            logger.error(f"Get image URL error: {e}")
            return None

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

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

            # Convert to RGB (JPEG doesn't support transparency)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background

            # Process each size
            processed_images = {}
            for size_name, (width, height) in self.image_sizes.items():
                # Resize image maintaining aspect ratio
                resized_image = ImageOps.fit(
                    image,
                    (width, height),
                    Image.Resampling.LANCZOS
                )

                # Save to bytes as JPEG
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

    async def _get_image_count(self, product_id: str) -> int:
        """Get current image count for product"""
        try:
            result = self.client.table("product_images").select(
                "id", count="exact"
            ).eq("product_id", product_id).execute()

            return result.count if result.count else 0

        except Exception as e:
            logger.error(f"Get image count error: {e}")
            return 0

    async def _create_image_record(
        self,
        product_id: str,
        image_url: str,
        thumbnail_url: str,
        display_order: int,
        is_primary: bool
    ) -> str:
        """Create image record in database"""
        try:
            image_data = {
                "product_id": product_id,
                "image_url": image_url,
                "thumbnail_url": thumbnail_url,
                "display_order": display_order,
                "is_primary": is_primary,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

            result = self.client.table("product_images").insert(image_data).execute()

            if not result.data:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create image record"
                )

            return result.data[0]['id']

        except Exception as e:
            logger.error(f"Create image record error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create image record in database"
            )

    async def _get_image_record(self, image_id: str) -> Optional[Dict]:
        """Get image record from database"""
        try:
            result = self.client.table("product_images").select("*").eq("id", image_id).execute()

            if result.data:
                return result.data[0]
            return None

        except Exception as e:
            logger.error(f"Get image record error: {e}")
            return None

    async def _get_all_images(self, product_id: str) -> List[Dict]:
        """Get all images for a product"""
        try:
            result = self.client.table("product_images").select("*").eq(
                "product_id", product_id
            ).order("display_order").execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Get all images error: {e}")
            return []

    async def _delete_image_record(self, image_id: str) -> None:
        """Delete image record from database"""
        try:
            result = self.client.table("product_images").delete().eq("id", image_id).execute()

            if not result.data:
                logger.warning(f"No image record deleted for ID: {image_id}")

        except Exception as e:
            logger.error(f"Delete image record error: {e}")
            raise

    async def _unset_other_primary_images(
        self,
        product_id: str,
        except_image_id: str
    ) -> None:
        """Unset primary flag for all other images"""
        try:
            self.client.table("product_images").update({
                "is_primary": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("product_id", product_id).neq("id", except_image_id).execute()

        except Exception as e:
            logger.error(f"Unset other primary images error: {e}")

    async def _set_first_image_as_primary(self, product_id: str) -> None:
        """Set first image as primary"""
        try:
            images = await self._get_all_images(product_id)
            if images:
                await self._update_image_primary(images[0]['id'], True)

        except Exception as e:
            logger.error(f"Set first image as primary error: {e}")

    async def _update_image_primary(self, image_id: str, is_primary: bool) -> None:
        """Update image primary flag"""
        try:
            self.client.table("product_images").update({
                "is_primary": is_primary,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", image_id).execute()

        except Exception as e:
            logger.error(f"Update image primary error: {e}")
            raise

    async def _update_image_order(self, image_id: str, display_order: int) -> None:
        """Update image display order"""
        try:
            self.client.table("product_images").update({
                "display_order": display_order,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", image_id).execute()

        except Exception as e:
            logger.error(f"Update image order error: {e}")
            raise

    def _extract_image_index(self, image_url: str) -> int:
        """Extract image index from URL"""
        try:
            # URL format: .../product_id/image_1_large.jpg
            filename = image_url.split('/')[-1]  # image_1_large.jpg
            parts = filename.split('_')          # ['image', '1', 'large.jpg']
            return int(parts[1])                 # 1
        except Exception as e:
            logger.error(f"Extract image index error: {e}")
            return 1

# Create service instance
product_image_service = ProductImageService()
