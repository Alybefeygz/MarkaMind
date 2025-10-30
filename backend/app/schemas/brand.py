from pydantic import BaseModel, ConfigDict, Field, validator
from datetime import datetime
from uuid import UUID
from typing import Optional
import re


class BrandCreate(BaseModel):
    """Schema for creating a new brand"""
    name: str = Field(..., min_length=2, max_length=100, description="Marka adı")
    description: Optional[str] = Field(None, max_length=500, description="Marka açıklaması")
    logo_url: Optional[str] = Field(None, description="Marka logo URL'i")
    theme_color: str = Field(default="#3B82F6", pattern=r'^#[0-9A-Fa-f]{6}$', description="Tema rengi (hex)")

    @validator('name')
    def validate_name(cls, v):
        """Validate brand name"""
        if not v or not v.strip():
            raise ValueError('Marka adı boş olamaz')
        if len(v.strip()) < 2:
            raise ValueError('Marka adı en az 2 karakter olmalıdır')
        return v.strip()

    @validator('theme_color')
    def validate_theme_color(cls, v):
        """Validate hex color"""
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Geçersiz renk kodu. Format: #RRGGBB')
        return v.upper()


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

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Marka adı boş olamaz')
            if len(v.strip()) < 2:
                raise ValueError('Marka adı en az 2 karakter olmalıdır')
            return v.strip()
        return v

    @validator('theme_color')
    def validate_theme_color(cls, v):
        if v is not None and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Geçersiz renk kodu. Format: #RRGGBB')
        return v.upper() if v else v


class BrandList(BaseModel):
    """Schema for brand list view"""
    id: UUID
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
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