from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserResponse(BaseModel):
    """API response schema for User"""
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, pattern=r'^(user|admin)$')


class UserProfile(BaseModel):
    """Public user profile schema"""
    id: UUID
    full_name: Optional[str] = None
    role: str
    
    model_config = ConfigDict(from_attributes=True)