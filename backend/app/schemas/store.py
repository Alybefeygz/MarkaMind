from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class StoreBase(BaseModel):
    """Base schema for Store"""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    logo: Optional[str] = None
    status: str = Field("draft", pattern="^(draft|active|inactive)$")
    platform: Optional[str] = Field(None, pattern="^(web|mobile|both)$")
    primary_color: str = Field("#000000", pattern="^#[0-9A-Fa-f]{6}$")
    secondary_color: str = Field("#FFFFFF", pattern="^#[0-9A-Fa-f]{6}$")
    text_color: str = Field("#000000", pattern="^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=200)
    custom_domain: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)


class StoreCreate(StoreBase):
    """Schema for creating a store"""
    brand_id: UUID

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Validate slug format"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only letters, numbers, hyphens, and underscores')
        return v.lower()


class StoreUpdate(BaseModel):
    """Schema for updating a store"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    logo: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|active|inactive)$")
    platform: Optional[str] = Field(None, pattern="^(web|mobile|both)$")
    primary_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    secondary_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    text_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=200)
    custom_domain: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class StoreResponse(StoreBase):
    """Schema for store response"""
    id: UUID
    brand_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StoreList(BaseModel):
    """Schema for store list item"""
    id: UUID
    brand_id: UUID
    name: str
    slug: str
    logo: Optional[str] = None
    status: str
    platform: Optional[str] = None
    primary_color: str
    secondary_color: str
    text_color: str
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StorePublic(BaseModel):
    """Schema for public store information"""
    id: UUID
    name: str
    slug: str
    logo: Optional[str] = None
    primary_color: str
    secondary_color: str
    text_color: str
    description: Optional[str] = None
    custom_domain: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StoreStats(BaseModel):
    """Schema for store statistics"""
    store_id: UUID
    total_products: int = 0
    active_products: int = 0
    total_reviews: int = 0
    average_rating: float = 0.0
    total_sales: int = 0

    model_config = ConfigDict(from_attributes=True)