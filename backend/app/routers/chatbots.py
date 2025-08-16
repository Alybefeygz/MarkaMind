from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from ..schemas.chatbot import ChatbotResponse, ChatbotUpdate, ChatbotList, ChatbotPublic
from ..schemas.common import StatusResponse, PaginationParams, PaginationResponse
from ..models.chatbot import ChatbotCreate
from ..dependencies import get_current_user, get_supabase_client

router = APIRouter(
    prefix="/chatbots",
    tags=["Chatbots"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=ChatbotResponse, status_code=status.HTTP_201_CREATED)
async def create_chatbot(
    chatbot: ChatbotCreate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Create a new chatbot for a brand
    """
    try:
        # Verify brand belongs to user
        brand_result = supabase.table("brands").select("id").eq("id", str(chatbot.brand_id)).eq("user_id", current_user["id"]).execute()
        
        if not brand_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found or not owned by user"
            )
        
        # Prepare chatbot data
        chatbot_data = chatbot.model_dump()
        
        # Create chatbot in database
        result = supabase.table("chatbots").insert(chatbot_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create chatbot"
            )
        
        return ChatbotResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chatbot: {str(e)}"
        )


@router.get("/", response_model=PaginationResponse[ChatbotList])
async def list_chatbots(
    pagination: PaginationParams = Depends(),
    brand_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get list of user's chatbots with pagination
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size
        
        # Build query - join with brands to ensure user ownership
        query = supabase.table("chatbots").select(
            "id, name, primary_color, status, created_at, brands!inner(user_id)",
            count="exact"
        ).eq("brands.user_id", current_user["id"])
        
        # Filter by brand if specified
        if brand_id:
            query = query.eq("brand_id", str(brand_id))
        
        # Get total count
        count_result = query.execute()
        total = count_result.count if count_result.count else 0
        
        # Get chatbots with pagination
        query = query.order(pagination.sort or "created_at", desc=True).range(offset, offset + pagination.size - 1)
        result = query.execute()
        
        # Process results to exclude brands field from response
        chatbots = []
        if result.data:
            for item in result.data:
                # Remove the brands field before creating ChatbotList
                chatbot_data = {k: v for k, v in item.items() if k != "brands"}
                chatbots.append(ChatbotList(**chatbot_data))
        
        return PaginationResponse(
            items=chatbots,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chatbots: {str(e)}"
        )


@router.get("/{chatbot_id}", response_model=ChatbotResponse)
async def get_chatbot(
    chatbot_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get a specific chatbot by ID
    """
    try:
        # Get chatbot with brand ownership check
        result = supabase.table("chatbots").select(
            "*, brands!inner(user_id)"
        ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Remove brands field from response
        chatbot_data = {k: v for k, v in result.data[0].items() if k != "brands"}
        return ChatbotResponse(**chatbot_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chatbot: {str(e)}"
        )


@router.put("/{chatbot_id}", response_model=ChatbotResponse)
async def update_chatbot(
    chatbot_id: UUID,
    chatbot_update: ChatbotUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update a specific chatbot
    """
    try:
        # Check if chatbot exists and user owns the brand
        existing = supabase.table("chatbots").select(
            "id, brands!inner(user_id)"
        ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Prepare update data
        update_data = chatbot_update.model_dump(exclude_unset=True)
        
        # Update chatbot
        result = supabase.table("chatbots").update(update_data).eq("id", str(chatbot_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update chatbot"
            )
        
        return ChatbotResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update chatbot: {str(e)}"
        )


@router.delete("/{chatbot_id}", response_model=StatusResponse)
async def delete_chatbot(
    chatbot_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete a specific chatbot
    """
    try:
        # Check if chatbot exists and user owns the brand
        existing = supabase.table("chatbots").select(
            "id, brands!inner(user_id)"
        ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Delete chatbot (cascade will handle related records)
        result = supabase.table("chatbots").delete().eq("id", str(chatbot_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete chatbot"
            )
        
        return StatusResponse(
            success=True,
            message="Chatbot deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chatbot: {str(e)}"
        )


@router.get("/script/{script_token}", response_model=ChatbotPublic)
async def get_chatbot_by_script_token(
    script_token: str,
    supabase = Depends(get_supabase_client)
):
    """
    Get public chatbot information by script token (no authentication required)
    """
    try:
        result = supabase.table("chatbots").select(
            "name, primary_color, secondary_color, script_token, language"
        ).eq("script_token", script_token).eq("status", "active").execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or inactive"
            )
        
        return ChatbotPublic(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chatbot: {str(e)}"
        )


@router.patch("/{chatbot_id}/activate", response_model=StatusResponse)
async def activate_chatbot(
    chatbot_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Activate a chatbot
    """
    try:
        # Check if chatbot exists and user owns the brand
        existing = supabase.table("chatbots").select(
            "id, brands!inner(user_id)"
        ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Activate chatbot
        result = supabase.table("chatbots").update({"status": "active"}).eq("id", str(chatbot_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to activate chatbot"
            )
        
        return StatusResponse(
            success=True,
            message="Chatbot activated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate chatbot: {str(e)}"
        )


@router.patch("/{chatbot_id}/deactivate", response_model=StatusResponse)
async def deactivate_chatbot(
    chatbot_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Deactivate a chatbot
    """
    try:
        # Check if chatbot exists and user owns the brand
        existing = supabase.table("chatbots").select(
            "id, brands!inner(user_id)"
        ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Deactivate chatbot
        result = supabase.table("chatbots").update({"status": "draft"}).eq("id", str(chatbot_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to deactivate chatbot"
            )
        
        return StatusResponse(
            success=True,
            message="Chatbot deactivated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate chatbot: {str(e)}"
        )


@router.get("/{chatbot_id}/regenerate-token", response_model=dict)
async def regenerate_script_token(
    chatbot_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Regenerate script token for a chatbot
    """
    try:
        # Check if chatbot exists and user owns the brand
        existing = supabase.table("chatbots").select(
            "id, brands!inner(user_id)"
        ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Generate new token - Supabase will auto-generate with uuid_generate_v4()
        import uuid
        new_token = str(uuid.uuid4())
        
        # Update chatbot with new token
        result = supabase.table("chatbots").update({"script_token": new_token}).eq("id", str(chatbot_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to regenerate token"
            )
        
        return {
            "success": True,
            "message": "Script token regenerated successfully",
            "script_token": new_token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate token: {str(e)}"
        )