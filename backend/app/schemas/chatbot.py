from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class ChatbotResponse(BaseModel):
    """API response schema for Chatbot"""
    id: UUID
    brand_id: UUID
    name: str
    avatar_url: Optional[str] = None
    primary_color: str
    secondary_color: str
    animation_style: str
    script_token: str
    language: str
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ChatbotUpdate(BaseModel):
    """Schema for updating chatbot information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    primary_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    secondary_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    animation_style: Optional[str] = Field(None, pattern=r'^(fade|slide|bounce|none)$')
    language: Optional[str] = Field(None, pattern=r'^(tr|en|de|fr|es)$')
    status: Optional[str] = Field(None, pattern=r'^(draft|active|inactive)$')


class ChatbotList(BaseModel):
    """Schema for chatbot list view"""
    id: UUID
    name: str
    avatar_url: Optional[str] = None
    primary_color: str
    status: str
    
    model_config = ConfigDict(from_attributes=True)


class ChatbotPublic(BaseModel):
    """Public chatbot schema for widgets"""
    name: str
    avatar_url: Optional[str] = None
    primary_color: str
    secondary_color: str
    script_token: str
    language: str = "tr"
    
    model_config = ConfigDict(from_attributes=True)