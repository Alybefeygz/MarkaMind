from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class ChatbotBase(BaseModel):
    """Base Chatbot model with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    primary_color: str = "#3B82F6"
    secondary_color: str = "#EF4444"
    animation_style: str = "fade"
    language: str = "tr"
    status: str = "draft"


class ChatbotCreate(ChatbotBase):
    """Chatbot model for creation requests"""
    brand_id: UUID


class Chatbot(ChatbotBase):
    """Complete Chatbot model with all fields"""
    id: UUID
    brand_id: UUID
    script_token: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)