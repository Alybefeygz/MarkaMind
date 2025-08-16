from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class BrandResponse(BaseModel):
    """API response schema for Brand"""
    id: UUID
    user_id: UUID
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    theme_color: str
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BrandUpdate(BaseModel):
    """Schema for updating brand information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = None
    theme_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_active: Optional[bool] = None


class BrandList(BaseModel):
    """Schema for brand list view"""
    id: UUID
    name: str
    slug: Optional[str] = None
    logo_url: Optional[str] = None
    theme_color: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class BrandPublic(BaseModel):
    """Public brand schema for widgets"""
    name: str
    logo_url: Optional[str] = None
    theme_color: str
    
    model_config = ConfigDict(from_attributes=True)