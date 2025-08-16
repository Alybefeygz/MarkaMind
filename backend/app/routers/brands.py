from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID

from ..schemas.brand import BrandResponse, BrandUpdate, BrandList, BrandPublic
from ..schemas.common import StatusResponse, PaginationParams, PaginationResponse
from ..models.brand import BrandCreate
from ..dependencies import get_current_user, get_supabase_client

router = APIRouter(
    prefix="/brands",
    tags=["Brands"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand: BrandCreate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Create a new brand for the current user
    """
    try:
        # Prepare brand data
        brand_data = brand.model_dump()
        brand_data["user_id"] = current_user["id"]
        
        # Create brand in database
        result = supabase.table("brands").insert(brand_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create brand"
            )
        
        return BrandResponse(**result.data[0])
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create brand: {str(e)}"
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
            "id, name, slug, theme_color, is_active, created_at"
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