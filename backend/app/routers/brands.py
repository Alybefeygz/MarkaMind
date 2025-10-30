from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import re

from ..schemas.brand import BrandResponse, BrandUpdate, BrandList, BrandPublic, BrandCreate
from ..schemas.common import StatusResponse, PaginationParams, PaginationResponse
from ..dependencies import get_current_user, get_supabase_client
from ..services.brand_logo_service import brand_logo_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/brands",
    tags=["Brands"],
    responses={404: {"description": "Not found"}}
)


def generate_slug(name: str) -> str:
    """Generate URL-safe slug from brand name"""
    turkish_map = {
        'ı': 'i', 'İ': 'i', 'ğ': 'g', 'Ğ': 'g',
        'ü': 'u', 'Ü': 'u', 'ş': 's', 'Ş': 's',
        'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c'
    }
    slug = name.lower()
    for tr_char, en_char in turkish_map.items():
        slug = slug.replace(tr_char, en_char)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    return slug.strip('-')


@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand: BrandCreate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Create a new brand for the current user

    - Slug otomatik oluşturulur
    - Slug benzersizlik kontrolü yapılır
    """
    try:
        # Generate slug
        base_slug = generate_slug(brand.name)
        slug = base_slug

        # Check slug uniqueness
        counter = 1
        while True:
            existing = supabase.table("brands").select("id").eq("slug", slug).execute()
            if not existing.data:
                break
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Prepare brand data
        brand_data = brand.model_dump()
        brand_data["user_id"] = current_user["id"]
        brand_data["slug"] = slug
        brand_data["created_at"] = datetime.utcnow().isoformat()
        brand_data["updated_at"] = datetime.utcnow().isoformat()

        # Create brand in database
        result = supabase.table("brands").insert(brand_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Marka oluşturulamadı"
            )

        logger.info(f"Brand created: {result.data[0]['id']} by user: {current_user['id']}")

        return BrandResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create brand error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Marka oluşturulurken hata: {str(e)}"
        )


@router.get("/", response_model=PaginationResponse[BrandList])
async def list_brands(
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get list of user's brands with pagination
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size
        
        # Get total count
        count_result = supabase.table("brands").select("id", count="exact").eq("user_id", current_user["id"]).execute()
        total = count_result.count if count_result.count else 0
        
        # Get brands with pagination
        query = supabase.table("brands").select(
            "id, name, slug, description, logo_url, theme_color, is_active, created_at"
        ).eq("user_id", current_user["id"]).order(pagination.sort or "created_at", desc=True)
        
        result = query.range(offset, offset + pagination.size - 1).execute()
        
        brands = [BrandList(**brand) for brand in result.data] if result.data else []
        
        return PaginationResponse(
            items=brands,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get brands: {str(e)}"
        )


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(
    brand_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get a specific brand by ID
    """
    try:
        result = supabase.table("brands").select("*").eq("id", str(brand_id)).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found"
            )
        
        return BrandResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get brand: {str(e)}"
        )


@router.put("/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_id: UUID,
    brand_update: BrandUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update a specific brand
    """
    try:
        # Check if brand exists and belongs to user
        existing = supabase.table("brands").select("id").eq("id", str(brand_id)).eq("user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found"
            )
        
        # Prepare update data
        update_data = brand_update.model_dump(exclude_unset=True)
        
        # Update brand
        result = supabase.table("brands").update(update_data).eq("id", str(brand_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update brand"
            )
        
        return BrandResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update brand: {str(e)}"
        )


@router.delete("/{brand_id}", response_model=StatusResponse)
async def delete_brand(
    brand_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete a specific brand
    """
    try:
        # Check if brand exists and belongs to user
        existing = supabase.table("brands").select("id").eq("id", str(brand_id)).eq("user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found"
            )
        
        # Check if brand has active chatbots
        chatbots = supabase.table("chatbots").select("id").eq("brand_id", str(brand_id)).execute()
        
        if chatbots.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete brand with existing chatbots"
            )
        
        # Delete brand
        result = supabase.table("brands").delete().eq("id", str(brand_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete brand"
            )
        
        return StatusResponse(
            success=True,
            message="Brand deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete brand: {str(e)}"
        )


@router.get("/{brand_id}/public", response_model=BrandPublic)
async def get_brand_public(
    brand_id: UUID,
    supabase = Depends(get_supabase_client)
):
    """
    Get public brand information (no authentication required)
    """
    try:
        result = supabase.table("brands").select("name, theme_color").eq("id", str(brand_id)).eq("is_active", True).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found or inactive"
            )
        
        return BrandPublic(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get brand: {str(e)}"
        )


@router.patch("/{brand_id}/activate", response_model=StatusResponse)
async def activate_brand(
    brand_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Activate a brand
    """
    try:
        # Check if brand exists and belongs to user
        existing = supabase.table("brands").select("id").eq("id", str(brand_id)).eq("user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found"
            )
        
        # Activate brand
        result = supabase.table("brands").update({"is_active": True}).eq("id", str(brand_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to activate brand"
            )
        
        return StatusResponse(
            success=True,
            message="Brand activated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate brand: {str(e)}"
        )


@router.patch("/{brand_id}/deactivate", response_model=StatusResponse)
async def deactivate_brand(
    brand_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Deactivate a brand
    """
    try:
        # Check if brand exists and belongs to user
        existing = supabase.table("brands").select("id").eq("id", str(brand_id)).eq("user_id", current_user["id"]).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found"
            )

        # Deactivate brand
        result = supabase.table("brands").update({"is_active": False}).eq("id", str(brand_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to deactivate brand"
            )

        return StatusResponse(
            success=True,
            message="Brand deactivated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate brand: {str(e)}"
        )


@router.get("/{brand_id}/stats", response_model=Dict[str, Any])
async def get_brand_stats(
    brand_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get brand statistics

    Returns:
    - total_stores: Toplam mağaza sayısı
    - active_stores: Aktif mağaza sayısı
    - total_chatbots: Toplam chatbot sayısı
    - active_chatbots: Yayında olan chatbot sayısı
    - total_products: Toplam ürün sayısı
    """
    try:
        # Check brand access
        brand_check = supabase.table("brands").select("id").eq("id", str(brand_id)).eq("user_id", current_user["id"]).execute()

        if not brand_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found"
            )

        # Stores count
        stores = supabase.table("stores").select("id, status").eq("brand_id", str(brand_id)).execute()
        total_stores = len(stores.data) if stores.data else 0
        active_stores = len([s for s in (stores.data or []) if s.get("status") == "active"])

        # Chatbots count
        chatbots = supabase.table("chatbots").select("id, status").eq("brand_id", str(brand_id)).execute()
        total_chatbots = len(chatbots.data) if chatbots.data else 0
        active_chatbots = len([c for c in (chatbots.data or []) if c.get("status") == "published"])

        # Products count
        total_products = 0
        if stores.data:
            for store in stores.data:
                products = supabase.table("products").select("id", count="exact").eq("store_id", store["id"]).execute()
                total_products += products.count if products.count else 0

        return {
            "total_stores": total_stores,
            "active_stores": active_stores,
            "total_chatbots": total_chatbots,
            "active_chatbots": active_chatbots,
            "total_products": total_products
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get brand stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"İstatistikler getirilirken hata: {str(e)}"
        )


@router.post("/{brand_id}/logo/upload", response_model=Dict[str, Any])
async def upload_brand_logo(
    brand_id: UUID,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Upload or update brand logo

    - Dosya tipi: JPG, PNG, WebP, SVG
    - Maksimum boyut: 2MB
    - Otomatik 4 farklı boyut oluşturulur: thumbnail, small, medium, large
    - Eski logo otomatik silinir
    - brands tablosundaki logo_url güncellenir
    """
    try:
        # Verify brand ownership FIRST
        brand_check = supabase.table("brands").select("id").eq("id", str(brand_id)).eq("user_id", current_user["id"]).execute()

        if not brand_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Marka bulunamadı veya size ait değil"
            )

        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp", "image/svg+xml"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sadece resim dosyaları yüklenebilir (JPEG, PNG, WebP, SVG)"
            )

        # Validate file size (max 2MB for logos)
        file_content = await file.read()
        if len(file_content) > 2 * 1024 * 1024:  # 2MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logo boyutu 2MB'dan küçük olmalıdır"
            )

        # Reset file pointer
        await file.seek(0)

        # Upload logo using service
        result = await brand_logo_service.upload_logo(
            brand_id=str(brand_id),
            file=file
        )

        logger.info(f"Brand logo uploaded: {brand_id} by user: {current_user['id']}")

        return {
            "message": "Logo başarıyla yüklendi",
            "logo_url": result["logo_url"],
            "sizes": result.get("sizes", {}),
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Brand logo upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logo yüklenirken bir hata oluştu"
        )


@router.delete("/{brand_id}/logo", response_model=StatusResponse)
async def delete_brand_logo(
    brand_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete brand logo

    - Tüm logo boyutları silinir (thumbnail, small, medium, large)
    - brands tablosundaki logo_url null yapılır
    """
    try:
        # Verify brand ownership
        brand_check = supabase.table("brands").select("id, logo_url").eq("id", str(brand_id)).eq("user_id", current_user["id"]).execute()

        if not brand_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Marka bulunamadı veya size ait değil"
            )

        # Check if logo exists
        if not brand_check.data[0].get("logo_url"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bu markaya ait logo bulunamadı"
            )

        # Delete logo
        result = await brand_logo_service.delete_logo(str(brand_id))

        logger.info(f"Brand logo deleted: {brand_id} by user: {current_user['id']}")

        return StatusResponse(
            success=True,
            message="Logo başarıyla silindi"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Brand logo delete failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logo silinirken bir hata oluştu"
        )


@router.get("/{brand_id}/logo", response_model=Dict[str, Any])
async def get_brand_logo(
    brand_id: UUID,
    size: str = Query("large", description="Logo boyutu: thumbnail, small, medium, large"),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get brand logo URL

    - size: thumbnail (64x64), small (128x128), medium (256x256), large (512x512)
    """
    try:
        # Verify brand ownership
        brand_check = supabase.table("brands").select("id, logo_url").eq("id", str(brand_id)).eq("user_id", current_user["id"]).execute()

        if not brand_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Marka bulunamadı veya size ait değil"
            )

        logo_url = await brand_logo_service.get_logo_url(str(brand_id), size)

        return {
            "logo_url": logo_url,
            "size": size,
            "brand_id": str(brand_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get brand logo failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logo bilgisi alınamadı"
        )