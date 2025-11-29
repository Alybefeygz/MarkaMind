from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.schemas.conversation import (
    ConversationStartRequest, 
    ConversationStartResponse
)
from app.dependencies import get_supabase_client

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("/start", response_model=ConversationStartResponse)
async def start_conversation(
    request: ConversationStartRequest,
    supabase = Depends(get_supabase_client)
):
    """
    Conversation başlat veya mevcut aktif conversation'ı döndür
    """
    try:
        # 1. Aktif conversation kontrol et
        active_conv = supabase.table("active_conversations").select(
            "conversation_id, conversations(id, message_count)"
        ).eq("session_id", request.session_id).eq(
            "chatbot_id", str(request.chatbot_id)
        ).execute()
        
        # Mevcut aktif conversation varsa döndür
        if active_conv.data:
            conv_data = active_conv.data[0]
            return ConversationStartResponse(
                conversation_id=conv_data["conversation_id"],
                is_new=False,
                message_count=conv_data["conversations"]["message_count"]
            )
        
        # 2. Yeni conversation oluştur
        new_conv = supabase.table("conversations").insert({
            "chatbot_id": str(request.chatbot_id),
            "session_id": request.session_id,
            "status": "active",
            "user_input": "",  # Placeholder
            "bot_response": ""  # Placeholder
        }).execute()
        
        if not new_conv.data:
            raise HTTPException(status_code=500, detail="Failed to create conversation")
        
        conversation_id = new_conv.data[0]["id"]
        
        # 3. active_conversations'a ekle
        supabase.table("active_conversations").insert({
            "session_id": request.session_id,
            "chatbot_id": str(request.chatbot_id),
            "conversation_id": conversation_id
        }).execute()
        
        return ConversationStartResponse(
            conversation_id=conversation_id,
            is_new=True,
            message_count=0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{conversation_id}/close")
async def close_conversation(
    conversation_id: UUID,
    supabase = Depends(get_supabase_client)
):
    """
    Conversation'ı kapat
    """
    try:
        # 1. Conversation'ı kapat
        supabase.table("conversations").update({
            "status": "closed",
            "closed_at": "now()"
        }).eq("id", str(conversation_id)).execute()
        
        # 2. active_conversations'dan kaldır
        supabase.table("active_conversations").delete().eq(
            "conversation_id", str(conversation_id)
        ).execute()
        
        return {"success": True, "message": "Conversation closed"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
