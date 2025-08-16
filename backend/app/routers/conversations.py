from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from typing import List, Optional
from uuid import UUID
import csv
import io

from ..schemas.conversation import ConversationResponse, ConversationList, ConversationStats
from ..schemas.common import PaginationParams, PaginationResponse
from ..dependencies import get_current_user, get_supabase_client

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=PaginationResponse[ConversationList])
async def list_conversations(
    pagination: PaginationParams = Depends(),
    chatbot_id: Optional[UUID] = None,
    session_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get list of conversations with pagination
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size
        
        # Build query - join with chatbots and brands to ensure user ownership
        query = supabase.table("conversations").select(
            "id, user_input, bot_response, latency_ms, created_at, chatbots!inner(brands!inner(user_id))",
            count="exact"
        ).eq("chatbots.brands.user_id", current_user["id"])
        
        # Apply filters
        if chatbot_id:
            query = query.eq("chatbot_id", str(chatbot_id))
        
        if session_id:
            query = query.eq("session_id", session_id)
        
        # Get total count
        count_result = query.execute()
        total = count_result.count if count_result.count else 0
        
        # Get conversations with pagination
        query = query.order(pagination.sort or "created_at", desc=True).range(offset, offset + pagination.size - 1)
        result = query.execute()
        
        # Process results to exclude nested fields from response
        conversations = []
        if result.data:
            for item in result.data:
                # Remove the nested fields and truncate messages for list view
                conversation_data = {k: v for k, v in item.items() if k != "chatbots"}
                # Truncate messages for list display (max 100 chars)
                if len(conversation_data.get("user_input", "")) > 100:
                    conversation_data["user_input"] = conversation_data["user_input"][:100] + "..."
                if len(conversation_data.get("bot_response", "")) > 100:
                    conversation_data["bot_response"] = conversation_data["bot_response"][:100] + "..."
                
                conversations.append(ConversationList(**conversation_data))
        
        return PaginationResponse(
            items=conversations,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversations: {str(e)}"
        )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get a specific conversation by ID
    """
    try:
        # Get conversation with ownership check
        result = supabase.table("conversations").select(
            "*, chatbots!inner(brands!inner(user_id))"
        ).eq("id", str(conversation_id)).eq("chatbots.brands.user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Remove nested fields from response
        conversation_data = {k: v for k, v in result.data[0].items() if k != "chatbots"}
        return ConversationResponse(**conversation_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation: {str(e)}"
        )


@router.get("/chatbot/{chatbot_id}/stats", response_model=ConversationStats)
async def get_chatbot_conversation_stats(
    chatbot_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get conversation statistics for a specific chatbot
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
        
        # Get conversation stats for this chatbot
        result = supabase.table("conversations").select(
            "latency_ms"
        ).eq("chatbot_id", str(chatbot_id)).execute()
        
        if not result.data:
            return ConversationStats(
                total_conversations=0,
                avg_latency=0.0,
                rating_avg=None
            )
        
        # Calculate statistics
        total_conversations = len(result.data)
        total_latency = sum(conv.get("latency_ms", 0) for conv in result.data)
        avg_latency = total_latency / total_conversations if total_conversations > 0 else 0.0
        
        # Get average rating from feedback
        feedback_result = supabase.table("feedback").select(
            "rating, conversations!inner(chatbot_id)"
        ).eq("conversations.chatbot_id", str(chatbot_id)).execute()
        
        rating_avg = None
        if feedback_result.data:
            ratings = [fb.get("rating", 0) for fb in feedback_result.data if fb.get("rating")]
            if ratings:
                rating_avg = sum(ratings) / len(ratings)
        
        return ConversationStats(
            total_conversations=total_conversations,
            avg_latency=avg_latency,
            rating_avg=rating_avg
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation stats: {str(e)}"
        )


@router.get("/chatbot/{chatbot_id}/sessions")
async def get_chatbot_sessions(
    chatbot_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get unique session IDs for a chatbot
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
        
        # Get unique session IDs with conversation count and latest activity
        result = supabase.rpc(
            "get_chatbot_sessions",
            {"chatbot_uuid": str(chatbot_id)}
        ).execute()
        
        # If RPC function doesn't exist, fallback to basic query
        if not hasattr(result, 'data') or result.data is None:
            # Fallback: get all conversations and group by session_id
            conversations = supabase.table("conversations").select(
                "session_id, created_at"
            ).eq("chatbot_id", str(chatbot_id)).order("created_at", desc=True).execute()
            
            # Group by session_id
            sessions = {}
            if conversations.data:
                for conv in conversations.data:
                    session_id = conv["session_id"]
                    if session_id not in sessions:
                        sessions[session_id] = {
                            "session_id": session_id,
                            "conversation_count": 0,
                            "latest_activity": conv["created_at"]
                        }
                    sessions[session_id]["conversation_count"] += 1
                    
                    # Update latest activity if this conversation is newer
                    if conv["created_at"] > sessions[session_id]["latest_activity"]:
                        sessions[session_id]["latest_activity"] = conv["created_at"]
            
            return {"sessions": list(sessions.values())}
        
        return {"sessions": result.data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chatbot sessions: {str(e)}"
        )


@router.get("/chatbot/{chatbot_id}/export")
async def export_conversations(
    chatbot_id: UUID,
    format: str = "csv",
    session_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Export conversations for a chatbot as CSV or JSON
    """
    try:
        # Verify chatbot belongs to user
        chatbot_result = supabase.table("chatbots").select(
            "id, name, brands!inner(user_id)"
        ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
        
        if not chatbot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or not owned by user"
            )
        
        chatbot_name = chatbot_result.data[0]["name"]
        
        # Build query
        query = supabase.table("conversations").select(
            "session_id, user_input, bot_response, latency_ms, created_at"
        ).eq("chatbot_id", str(chatbot_id)).order("created_at", desc=False)
        
        # Apply session filter if provided
        if session_id:
            query = query.eq("session_id", session_id)
        
        result = query.execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No conversations found for export"
            )
        
        if format.lower() == "csv":
            # Create CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "session_id", "user_input", "bot_response", "latency_ms", "created_at"
            ])
            writer.writeheader()
            writer.writerows(result.data)
            
            # Prepare response
            output.seek(0)
            filename = f"{chatbot_name}_conversations_{session_id if session_id else 'all'}.csv"
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode('utf-8')),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        elif format.lower() == "json":
            import json
            
            # Create JSON
            json_data = json.dumps(result.data, indent=2, default=str)
            filename = f"{chatbot_name}_conversations_{session_id if session_id else 'all'}.json"
            
            return StreamingResponse(
                io.BytesIO(json_data.encode('utf-8')),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported export format. Use 'csv' or 'json'"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export conversations: {str(e)}"
        )


@router.delete("/session/{session_id}", response_model=dict)
async def delete_session_conversations(
    session_id: str,
    chatbot_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete all conversations in a session
    """
    try:
        # Build query to find conversations in the session
        if chatbot_id:
            # Verify chatbot belongs to user first
            chatbot_result = supabase.table("chatbots").select(
                "id, brands!inner(user_id)"
            ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
            
            if not chatbot_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chatbot not found or not owned by user"
                )
            
            # Delete conversations for specific chatbot and session
            result = supabase.table("conversations").delete().eq(
                "session_id", session_id
            ).eq("chatbot_id", str(chatbot_id)).execute()
        else:
            # Delete conversations across all user's chatbots for this session
            # First get all user's chatbot IDs
            user_chatbots = supabase.table("chatbots").select(
                "id, brands!inner(user_id)"
            ).eq("brands.user_id", current_user["id"]).execute()
            
            if not user_chatbots.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No chatbots found for user"
                )
            
            chatbot_ids = [cb["id"] for cb in user_chatbots.data]
            
            # Delete conversations
            result = supabase.table("conversations").delete().eq(
                "session_id", session_id
            ).in_("chatbot_id", chatbot_ids).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No conversations found for the specified session"
            )
        
        return {
            "success": True,
            "message": f"Deleted {len(result.data)} conversations from session {session_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session conversations: {str(e)}"
        )