from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

from ..schemas.conversation import FeedbackResponse
from ..schemas.common import StatusResponse, PaginationParams, PaginationResponse
from ..dependencies import get_current_user, get_supabase_client

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
    responses={404: {"description": "Not found"}}
)


class FeedbackCreate(BaseModel):
    """Request model for creating feedback"""
    conversation_id: UUID
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional comment")


class FeedbackUpdate(BaseModel):
    """Request model for updating feedback"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional comment")


class FeedbackList(BaseModel):
    """List view schema for feedback"""
    id: UUID
    conversation_id: UUID
    rating: int
    comment: Optional[str] = None
    created_at: str
    user_input: Optional[str] = None  # From related conversation
    bot_response: Optional[str] = None  # From related conversation


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback: FeedbackCreate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Create feedback for a conversation
    """
    try:
        # Verify conversation exists and belongs to user's chatbot
        conv_result = supabase.table("conversations").select(
            "id, chatbots!inner(brands!inner(user_id))"
        ).eq("id", str(feedback.conversation_id)).eq("chatbots.brands.user_id", current_user["id"]).execute()
        
        if not conv_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or not owned by user"
            )
        
        # Check if feedback already exists for this conversation
        existing_feedback = supabase.table("feedback").select("id").eq("conversation_id", str(feedback.conversation_id)).execute()
        
        if existing_feedback.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback already exists for this conversation"
            )
        
        # Create feedback
        feedback_data = feedback.model_dump()
        feedback_data["conversation_id"] = str(feedback.conversation_id)
        
        result = supabase.table("feedback").insert(feedback_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create feedback"
            )
        
        return FeedbackResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create feedback: {str(e)}"
        )


@router.get("/", response_model=PaginationResponse[FeedbackList])
async def list_feedback(
    pagination: PaginationParams = Depends(),
    chatbot_id: Optional[UUID] = None,
    rating_filter: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get list of feedback with pagination
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size
        
        # Build query - join with conversations, chatbots and brands to ensure user ownership
        query = supabase.table("feedback").select(
            "id, conversation_id, rating, comment, created_at, conversations!inner(user_input, bot_response, chatbots!inner(brands!inner(user_id)))",
            count="exact"
        ).eq("conversations.chatbots.brands.user_id", current_user["id"])
        
        # Apply filters
        if chatbot_id:
            query = query.eq("conversations.chatbot_id", str(chatbot_id))
        
        if rating_filter:
            query = query.eq("rating", rating_filter)
        
        # Get total count
        count_result = query.execute()
        total = count_result.count if count_result.count else 0
        
        # Get feedback with pagination
        query = query.order(pagination.sort or "created_at", desc=True).range(offset, offset + pagination.size - 1)
        result = query.execute()
        
        # Process results to create proper response format
        feedback_list = []
        if result.data:
            for item in result.data:
                conversation_data = item.get("conversations", {})
                feedback_data = {
                    "id": item["id"],
                    "conversation_id": item["conversation_id"],
                    "rating": item["rating"],
                    "comment": item["comment"],
                    "created_at": item["created_at"],
                    "user_input": conversation_data.get("user_input", "")[:100] + "..." if len(conversation_data.get("user_input", "")) > 100 else conversation_data.get("user_input"),
                    "bot_response": conversation_data.get("bot_response", "")[:100] + "..." if len(conversation_data.get("bot_response", "")) > 100 else conversation_data.get("bot_response")
                }
                feedback_list.append(FeedbackList(**feedback_data))
        
        return PaginationResponse(
            items=feedback_list,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback: {str(e)}"
        )


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get a specific feedback by ID
    """
    try:
        # Get feedback with ownership check
        result = supabase.table("feedback").select(
            "*, conversations!inner(chatbots!inner(brands!inner(user_id)))"
        ).eq("id", str(feedback_id)).eq("conversations.chatbots.brands.user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        # Remove nested fields from response
        feedback_data = {k: v for k, v in result.data[0].items() if k != "conversations"}
        return FeedbackResponse(**feedback_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback: {str(e)}"
        )


@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: UUID,
    feedback_update: FeedbackUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update a specific feedback (limited functionality)
    """
    try:
        # Check if feedback exists and user owns it
        existing = supabase.table("feedback").select(
            "id, conversations!inner(chatbots!inner(brands!inner(user_id)))"
        ).eq("id", str(feedback_id)).eq("conversations.chatbots.brands.user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        # Prepare update data
        update_data = feedback_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided for update"
            )
        
        # Update feedback
        result = supabase.table("feedback").update(update_data).eq("id", str(feedback_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update feedback"
            )
        
        return FeedbackResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update feedback: {str(e)}"
        )


@router.delete("/{feedback_id}", response_model=StatusResponse)
async def delete_feedback(
    feedback_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete a specific feedback
    """
    try:
        # Check if feedback exists and user owns it
        existing = supabase.table("feedback").select(
            "id, conversations!inner(chatbots!inner(brands!inner(user_id)))"
        ).eq("id", str(feedback_id)).eq("conversations.chatbots.brands.user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        # Delete feedback
        result = supabase.table("feedback").delete().eq("id", str(feedback_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete feedback"
            )
        
        return StatusResponse(
            success=True,
            message="Feedback deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete feedback: {str(e)}"
        )


@router.get("/chatbot/{chatbot_id}/stats")
async def get_chatbot_feedback_stats(
    chatbot_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get feedback statistics for a specific chatbot
    """
    try:
        # Verify chatbot belongs to user
        chatbot_result = supabase.table("chatbots").select(
            "id, brands!inner(user_id)"
        ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
        
        if not chatbot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or not owned by user"
            )
        
        # Get feedback statistics for this chatbot
        result = supabase.table("feedback").select(
            "rating, conversations!inner(chatbot_id)"
        ).eq("conversations.chatbot_id", str(chatbot_id)).execute()
        
        if not result.data:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "rating_distribution": {
                    "1": 0, "2": 0, "3": 0, "4": 0, "5": 0
                }
            }
        
        # Calculate statistics
        total_feedback = len(result.data)
        ratings = [fb["rating"] for fb in result.data]
        average_rating = sum(ratings) / total_feedback if total_feedback > 0 else 0.0
        
        # Rating distribution
        rating_distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        for rating in ratings:
            rating_distribution[str(rating)] += 1
        
        return {
            "total_feedback": total_feedback,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback stats: {str(e)}"
        )


@router.get("/conversation/{conversation_id}", response_model=FeedbackResponse)
async def get_feedback_by_conversation(
    conversation_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get feedback for a specific conversation
    """
    try:
        # Verify conversation belongs to user and get feedback
        result = supabase.table("feedback").select(
            "*, conversations!inner(chatbots!inner(brands!inner(user_id)))"
        ).eq("conversation_id", str(conversation_id)).eq("conversations.chatbots.brands.user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found for this conversation"
            )
        
        # Remove nested fields from response
        feedback_data = {k: v for k, v in result.data[0].items() if k != "conversations"}
        return FeedbackResponse(**feedback_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback: {str(e)}"
        )


@router.post("/batch-delete", response_model=StatusResponse)
async def batch_delete_feedback(
    feedback_ids: List[UUID],
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete multiple feedback entries at once
    """
    try:
        if not feedback_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No feedback IDs provided"
            )
        
        # Convert UUIDs to strings
        id_strings = [str(fid) for fid in feedback_ids]
        
        # Verify all feedback entries belong to the user
        existing = supabase.table("feedback").select(
            "id, conversations!inner(chatbots!inner(brands!inner(user_id)))"
        ).in_("id", id_strings).eq("conversations.chatbots.brands.user_id", current_user["id"]).execute()
        
        if not existing.data or len(existing.data) != len(feedback_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more feedback entries not found or not owned by user"
            )
        
        # Delete all feedback entries
        result = supabase.table("feedback").delete().in_("id", id_strings).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete feedback entries"
            )
        
        return StatusResponse(
            success=True,
            message=f"Successfully deleted {len(result.data)} feedback entries"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch delete feedback: {str(e)}"
        )