from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import List, Optional
from uuid import UUID

from ..schemas.store import (
    StoreResponse, StoreCreate, StoreUpdate, StoreList,
    StorePublic, StoreStats
)
from ..schemas.chatbox import ChatboxResponse
from ..schemas.common import StatusResponse, PaginationParams, PaginationResponse
from ..dependencies import get_current_user, get_supabase_client
from ..services.store_logo_service import store_logo_service

router = APIRouter(
    prefix="/stores",
    tags=["Stores"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
async def create_store(
    store: StoreCreate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Create a new store for a brand
    """
    try:
        # Verify brand belongs to user
        brand_result = supabase.table("brands").select("id").eq(
            "id", str(store.brand_id)
        ).eq("user_id", current_user["id"]).execute()

        if not brand_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found or you don't have permission"
            )

        # Check if slug is unique
        slug_check = supabase.table("stores").select("id").eq("slug", store.slug).execute()
        if slug_check.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Store with this slug already exists"
            )

        # Prepare store data
        store_data = store.model_dump()
        store_data["brand_id"] = str(store.brand_id)

        # Create store in database
        result = supabase.table("stores").insert(store_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create store"
            )

        return StoreResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create store: {str(e)}"
        )


@router.get("/", response_model=PaginationResponse[StoreList])
async def list_stores(
    brand_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get list of user's stores with pagination and filters
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size

        # Build query - get stores through brands
        query = supabase.table("stores").select(
            "*, brands!inner(user_id)",
            count="exact"
        ).eq("brands.user_id", current_user["id"])

        # Apply filters
        if brand_id:
            query = query.eq("brand_id", str(brand_id))
        if status_filter:
            query = query.eq("status", status_filter)

        # Get total count
        count_result = query.execute()
        total = count_result.count if count_result.count else 0

        # Get stores with pagination
        query = query.order(pagination.sort or "created_at", desc=True)
        result = query.range(offset, offset + pagination.size - 1).execute()

        # Transform data - remove nested brands object
        stores_data = []
        for store in result.data if result.data else []:
            store_copy = store.copy()
            store_copy.pop('brands', None)
            stores_data.append(StoreList(**store_copy))

        return PaginationResponse(
            items=stores_data,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stores: {str(e)}"
        )


@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(
    store_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get a specific store by ID
    """
    try:
        # Get store with brand user_id check
        result = supabase.table("stores").select(
            "*, brands!inner(user_id)"
        ).eq("id", str(store_id)).eq("brands.user_id", current_user["id"]).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )

        store_data = result.data[0].copy()
        store_data.pop('brands', None)

        return StoreResponse(**store_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get store: {str(e)}"
        )


@router.put("/{store_id}", response_model=StoreResponse)
async def update_store(
    store_id: UUID,
    store_update: StoreUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update a specific store
    """
    try:
        # Check if store exists and belongs to user
        existing = supabase.table("stores").select(
            "*, brands!inner(user_id)"
        ).eq("id", str(store_id)).eq("brands.user_id", current_user["id"]).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )

        # Check slug uniqueness if updating slug
        update_data = store_update.model_dump(exclude_unset=True)
        if "slug" in update_data:
            slug_check = supabase.table("stores").select("id").eq(
                "slug", update_data["slug"]
            ).neq("id", str(store_id)).execute()

            if slug_check.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Store with this slug already exists"
                )

        # Update store
        result = supabase.table("stores").update(update_data).eq("id", str(store_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update store"
            )

        return StoreResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update store: {str(e)}"
        )


@router.delete("/{store_id}", response_model=StatusResponse)
async def delete_store(
    store_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete a specific store
    """
    try:
        # Check if store exists and belongs to user
        existing = supabase.table("stores").select(
            "*, brands!inner(user_id)"
        ).eq("id", str(store_id)).eq("brands.user_id", current_user["id"]).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )

        # Check if store has products
        products = supabase.table("products").select("id").eq("store_id", str(store_id)).execute()

        if products.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete store with existing products"
            )

        # Delete store
        result = supabase.table("stores").delete().eq("id", str(store_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete store"
            )

        return StatusResponse(
            success=True,
            message="Store deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete store: {str(e)}"
        )


@router.get("/{store_id}/stats", response_model=StoreStats)
async def get_store_stats(
    store_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get store statistics
    """
    try:
        # Check if store belongs to user
        store_check = supabase.table("stores").select(
            "*, brands!inner(user_id)"
        ).eq("id", str(store_id)).eq("brands.user_id", current_user["id"]).execute()

        if not store_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )

        # Get product statistics
        products = supabase.table("products").select(
            "id, status, average_rating, review_count, sales_count"
        ).eq("store_id", str(store_id)).execute()

        total_products = len(products.data) if products.data else 0
        active_products = len([p for p in products.data if p["status"] == "active"]) if products.data else 0

        # Calculate aggregates
        total_reviews = sum(p.get("review_count", 0) for p in products.data) if products.data else 0
        total_sales = sum(p.get("sales_count", 0) for p in products.data) if products.data else 0

        # Calculate average rating across all products
        ratings = [float(p.get("average_rating", 0)) for p in products.data if p.get("average_rating", 0) > 0] if products.data else []
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0

        return StoreStats(
            store_id=store_id,
            total_products=total_products,
            active_products=active_products,
            total_reviews=total_reviews,
            average_rating=round(average_rating, 2),
            total_sales=total_sales
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get store stats: {str(e)}"
        )


@router.patch("/{store_id}/activate", response_model=StatusResponse)
async def activate_store(
    store_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Activate a store
    """
    try:
        # Check if store exists and belongs to user
        existing = supabase.table("stores").select(
            "*, brands!inner(user_id)"
        ).eq("id", str(store_id)).eq("brands.user_id", current_user["id"]).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )

        # Activate store
        result = supabase.table("stores").update({"status": "active"}).eq("id", str(store_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to activate store"
            )

        return StatusResponse(
            success=True,
            message="Store activated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate store: {str(e)}"
        )


@router.patch("/{store_id}/deactivate", response_model=StatusResponse)
async def deactivate_store(
    store_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Deactivate a store
    """
    try:
        # Check if store exists and belongs to user
        existing = supabase.table("stores").select(
            "*, brands!inner(user_id)"
        ).eq("id", str(store_id)).eq("brands.user_id", current_user["id"]).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found"
            )

        # Deactivate store
        result = supabase.table("stores").update({"status": "inactive"}).eq("id", str(store_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to deactivate store"
            )

        return StatusResponse(
            success=True,
            message="Store deactivated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate store: {str(e)}"
        )


# ============================================================================
# STORE LOGO ENDPOINTS
# ============================================================================

@router.post("/{store_id}/logo/upload")
async def upload_store_logo(
    store_id: UUID,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Upload store logo

    - Validates store ownership
    - Uploads logo to storage (4 sizes: thumbnail, small, medium, large)
    - Returns logo URLs for all sizes
    - Supported formats: PNG, JPG, SVG, WebP
    - Max file size: 2MB
    """
    try:
        # Verify store belongs to user (through brand)
        store_check = supabase.table("stores").select(
            "*, brands!inner(user_id)"
        ).eq("id", str(store_id)).eq("brands.user_id", current_user["id"]).execute()

        if not store_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found or you don't have permission"
            )

        # Upload logo
        result = await store_logo_service.upload_logo(str(store_id), file)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload logo: {str(e)}"
        )


@router.delete("/{store_id}/logo", response_model=StatusResponse)
async def delete_store_logo(
    store_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete store logo

    - Validates store ownership
    - Deletes logo from storage (all sizes)
    - Updates database
    """
    try:
        # Verify store belongs to user (through brand)
        store_check = supabase.table("stores").select(
            "*, brands!inner(user_id)"
        ).eq("id", str(store_id)).eq("brands.user_id", current_user["id"]).execute()

        if not store_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found or you don't have permission"
            )

        # Delete logo
        result = await store_logo_service.delete_logo(str(store_id))

        return StatusResponse(
            success=True,
            message=result["message"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete logo: {str(e)}"
        )


@router.get("/{store_id}/logo/{size}")
async def get_store_logo_url(
    store_id: UUID,
    size: str = "large",
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get store logo URL for specific size

    - Validates store ownership
    - Returns logo URL for requested size
    - Available sizes: thumbnail (64px), small (128px), medium (256px), large (512px)
    """
    try:
        # Verify store belongs to user (through brand)
        store_check = supabase.table("stores").select(
            "*, brands!inner(user_id)"
        ).eq("id", str(store_id)).eq("brands.user_id", current_user["id"]).execute()

        if not store_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found or you don't have permission"
            )

        # Get logo URL
        logo_url = await store_logo_service.get_logo_url(str(store_id), size)

        if not logo_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Logo not found"
            )

        return {"logo_url": logo_url, "size": size}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get logo URL: {str(e)}"
        )


@router.get("/{store_id}/chatbox", response_model=ChatboxResponse)
async def get_store_chatbox(
    store_id: UUID,
    supabase = Depends(get_supabase_client)
):
    """
    Get active chatbox for a specific store (public endpoint for virtual store pages)

    Returns the chatbox configuration if:
    - Store exists and is active
    - Chatbox is integrated with the store
    - Chatbox status is 'active'
    - Integration is active (is_active = true)
    """
    try:
        # Get chatbox integrated with this store
        result = supabase.table("chatbox_stores").select(
            "chatbox_id, show_on_homepage, show_on_products, position, is_active, chatbots!chatbox_id(*)"
        ).eq("store_id", str(store_id)).eq(
            "is_active", True
        ).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active chatbox found for this store"
            )

        relation = result.data[0]
        chatbox_data = relation.get('chatbots')

        if not chatbox_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbox not found"
            )

        # Check if chatbox is active
        if chatbox_data.get('status') != 'active':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbox is not active"
            )

        # Add integration settings to response
        chatbox_data['show_on_homepage'] = relation['show_on_homepage']
        chatbox_data['show_on_products'] = relation['show_on_products']
        chatbox_data['position'] = relation['position']

        # Add counts (for compatibility with ChatboxResponse schema)
        chatbox_data['store_count'] = 0
        chatbox_data['product_count'] = 0
        chatbox_data['conversation_count'] = 0
        chatbox_data['knowledge_source_count'] = 0

        return ChatboxResponse(**chatbox_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get store chatbox: {str(e)}"
        )