from pydantic import BaseModel
from typing import Optional

class UserProfile(BaseModel):
    """Kullanıcı profil bilgileri"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class UserSessionResponse(BaseModel):
    """User session yanıtı"""
    user_profile: dict
    extracted_entities: dict

class UserSessionUpdateRequest(BaseModel):
    """User session güncelleme isteği"""
    user_profile: UserProfile
