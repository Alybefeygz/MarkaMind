from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
import uuid
from datetime import datetime, timedelta

from ..schemas.conversation import ChatWidgetMessage
from ..schemas.chatbot import ChatbotPublic
from ..schemas.brand import BrandPublic
from ..dependencies import get_supabase_client

router = APIRouter(
    prefix="/widget",
    tags=["Widget API"],
    responses={404: {"description": "Not found"}}
)


class ChatRequest(BaseModel):
    """Request model for chat interactions"""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat interactions"""
    message: str
    session_id: str
    timestamp: datetime


class WidgetConfig(BaseModel):
    """Widget configuration response"""
    chatbot: ChatbotPublic
    brand: BrandPublic
    script_token: str


@router.get("/config/{script_token}", response_model=WidgetConfig)
async def get_widget_config(
    script_token: str,
    supabase = Depends(get_supabase_client)
):
    """
    Get widget configuration by script token (public endpoint)
    """
    try:
        # Get chatbot and brand information by script token
        result = supabase.table("chatbots").select(
            "name, primary_color, secondary_color, script_token, language, brands!inner(name, theme_color)"
        ).eq("script_token", script_token).eq("status", "active").execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found or inactive"
            )
        
        chatbot_data = result.data[0]
        brand_data = chatbot_data.pop("brands")
        
        return WidgetConfig(
            chatbot=ChatbotPublic(**chatbot_data),
            brand=BrandPublic(**brand_data),
            script_token=script_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget config: {str(e)}"
        )


@router.post("/chat/{script_token}", response_model=ChatResponse)
async def chat_with_widget(
    script_token: str,
    chat_request: ChatRequest,
    supabase = Depends(get_supabase_client)
):
    """
    Send a message to the chatbot widget (public endpoint)
    """
    try:
        # Get chatbot by script token
        chatbot_result = supabase.table("chatbots").select(
            "id, name, status"
        ).eq("script_token", script_token).eq("status", "active").execute()
        
        if not chatbot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or inactive"
            )
        
        chatbot = chatbot_result.data[0]
        chatbot_id = chatbot["id"]
        
        # Generate or use provided session ID
        session_id = chat_request.session_id or str(uuid.uuid4())
        
        # For now, return a simple echo response
        # In a real implementation, this would integrate with OpenRouter or another AI service
        bot_response = f"Hello! You said: '{chat_request.message}'. I'm {chatbot['name']} and I'm here to help!"
        
        # Store conversation in database
        conversation_data = {
            "chatbot_id": chatbot_id,
            "session_id": session_id,
            "user_input": chat_request.message,
            "bot_response": bot_response,
            "latency_ms": 100,  # Placeholder latency
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Insert conversation
        supabase.table("conversations").insert(conversation_data).execute()
        
        return ChatResponse(
            message=bot_response,
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/history/{script_token}/{session_id}", response_model=List[ChatWidgetMessage])
async def get_chat_history(
    script_token: str,
    session_id: str,
    limit: int = 50,
    supabase = Depends(get_supabase_client)
):
    """
    Get chat history for a session (public endpoint)
    """
    try:
        # Verify chatbot exists and is active
        chatbot_result = supabase.table("chatbots").select(
            "id"
        ).eq("script_token", script_token).eq("status", "active").execute()
        
        if not chatbot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or inactive"
            )
        
        chatbot_id = chatbot_result.data[0]["id"]
        
        # Get conversation history
        result = supabase.table("conversations").select(
            "user_input, bot_response, created_at"
        ).eq("chatbot_id", chatbot_id).eq("session_id", session_id).order(
            "created_at", desc=False
        ).limit(limit).execute()
        
        if not result.data:
            return []
        
        # Convert to chat widget messages format
        messages = []
        for conv in result.data:
            # Add user message
            messages.append(ChatWidgetMessage(
                message=conv["user_input"],
                timestamp=datetime.fromisoformat(conv["created_at"].replace("Z", "+00:00")),
                is_user=True
            ))
            
            # Add bot message
            messages.append(ChatWidgetMessage(
                message=conv["bot_response"],
                timestamp=datetime.fromisoformat(conv["created_at"].replace("Z", "+00:00")),
                is_user=False
            ))
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat history: {str(e)}"
        )


@router.get("/health/{script_token}")
async def check_widget_health(
    script_token: str,
    supabase = Depends(get_supabase_client)
):
    """
    Check if widget is active and healthy (public endpoint)
    """
    try:
        # Check if chatbot exists and is active
        result = supabase.table("chatbots").select(
            "id, name, status"
        ).eq("script_token", script_token).execute()
        
        if not result.data:
            return {
                "status": "not_found",
                "active": False,
                "message": "Widget not found"
            }
        
        chatbot = result.data[0]
        is_active = chatbot["status"] == "active"
        
        return {
            "status": "active" if is_active else "inactive",
            "active": is_active,
            "chatbot_name": chatbot["name"],
            "message": "Widget is ready" if is_active else "Widget is not active"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "active": False,
            "message": f"Error checking widget health: {str(e)}"
        }


@router.post("/feedback/{script_token}")
async def submit_widget_feedback(
    script_token: str,
    conversation_id: UUID,
    rating: int,
    comment: Optional[str] = None,
    supabase = Depends(get_supabase_client)
):
    """
    Submit feedback for a conversation (public endpoint)
    """
    try:
        # Verify chatbot exists and is active
        chatbot_result = supabase.table("chatbots").select(
            "id"
        ).eq("script_token", script_token).eq("status", "active").execute()
        
        if not chatbot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or inactive"
            )
        
        chatbot_id = chatbot_result.data[0]["id"]
        
        # Verify conversation exists and belongs to this chatbot
        conv_result = supabase.table("conversations").select(
            "id"
        ).eq("id", str(conversation_id)).eq("chatbot_id", chatbot_id).execute()
        
        if not conv_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Validate rating
        if not (1 <= rating <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        
        # Submit feedback
        feedback_data = {
            "conversation_id": str(conversation_id),
            "rating": rating,
            "comment": comment
        }
        
        result = supabase.table("feedback").insert(feedback_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to submit feedback"
            )
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": result.data[0]["id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/embed/{script_token}")
async def get_embed_code(
    script_token: str,
    supabase = Depends(get_supabase_client)
):
    """
    Get embed code for the widget (public endpoint)
    """
    try:
        # Verify chatbot exists and is active
        result = supabase.table("chatbots").select(
            "id, name"
        ).eq("script_token", script_token).eq("status", "active").execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found or inactive"
            )
        
        # Generate embed code
        embed_code = f"""
<!-- MarkaMind Chatbot Widget -->
<div id="markamind-widget-{script_token}"></div>
<script>
(function() {{
    var script = document.createElement('script');
    script.src = 'https://your-domain.com/widget/js/{script_token}';
    script.async = true;
    document.head.appendChild(script);
}})();
</script>
<!-- End MarkaMind Chatbot Widget -->
        """.strip()
        
        return {
            "script_token": script_token,
            "chatbot_name": result.data[0]["name"],
            "embed_code": embed_code,
            "instructions": "Copy and paste this code into your website's HTML where you want the chatbot to appear."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get embed code: {str(e)}"
        )


@router.get("/stats/{script_token}")
async def get_widget_stats(
    script_token: str,
    supabase = Depends(get_supabase_client)
):
    """
    Get basic usage statistics for widget (public endpoint with limited data)
    """
    try:
        # Verify chatbot exists and is active
        chatbot_result = supabase.table("chatbots").select(
            "id, name"
        ).eq("script_token", script_token).eq("status", "active").execute()
        
        if not chatbot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found or inactive"
            )
        
        chatbot_id = chatbot_result.data[0]["id"]
        
        # Get conversation count (last 7 days)
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        conv_result = supabase.table("conversations").select(
            "id", count="exact"
        ).eq("chatbot_id", chatbot_id).gte("created_at", seven_days_ago).execute()
        
        conversation_count = conv_result.count if conv_result.count else 0
        
        # Get unique sessions count (last 7 days)
        session_result = supabase.table("conversations").select(
            "session_id"
        ).eq("chatbot_id", chatbot_id).gte("created_at", seven_days_ago).execute()
        
        unique_sessions = len(set(conv["session_id"] for conv in session_result.data)) if session_result.data else 0
        
        return {
            "chatbot_name": chatbot_result.data[0]["name"],
            "conversations_last_7_days": conversation_count,
            "unique_sessions_last_7_days": unique_sessions,
            "status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget stats: {str(e)}"
        )