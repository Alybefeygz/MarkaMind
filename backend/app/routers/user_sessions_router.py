from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user_session import (
    UserSessionResponse, 
    UserSessionUpdateRequest
)
from app.dependencies import get_supabase_client

router = APIRouter(tags=["user_sessions"])

@router.get("/{session_id}/profile", response_model=UserSessionResponse)
async def get_user_profile(
    session_id: str,
    supabase = Depends(get_supabase_client)
):
    """
    Kullanıcı profil bilgilerini getir
    """
    try:
        result = supabase.table("user_sessions").select(
            "user_profile"
        ).eq("session_id", session_id).execute()
        
        if result.data:
            return UserSessionResponse(
                user_profile=result.data[0].get("user_profile", {}),
                extracted_entities={}
            )
        
        # Session yoksa boş döndür
        return UserSessionResponse(
            user_profile={},
            extracted_entities={}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/profile")
async def update_user_profile(
    session_id: str,
    request: UserSessionUpdateRequest,
    supabase = Depends(get_supabase_client)
):
    """
    Kullanıcı profil bilgilerini güncelle
    """
    try:
        # Upsert: Varsa güncelle, yoksa oluştur
        supabase.table("user_sessions").upsert({
            "session_id": session_id,
            "user_profile": request.user_profile.dict(),
            "last_seen_at": "now()"
        }, on_conflict="session_id").execute()
        
        return {"success": True, "message": "Profile updated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
