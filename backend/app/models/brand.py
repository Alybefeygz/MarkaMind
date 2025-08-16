from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class BrandBase(BaseModel):
    """Base Brand model with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    slug: Optional[str] = Field(None, pattern=r'^[a-z0-9-]+$', max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = None
    theme_color: str = "#3B82F6"
    is_active: bool = True


class BrandCreate(BrandBase):
    """Brand model for creation requests"""
    pass


class Brand(BrandBase):
    """Complete Brand model with all fields"""
    id: UUID
    user_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)