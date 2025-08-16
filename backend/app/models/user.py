from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserBase(BaseModel):
    """Base User model with common fields"""
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"


class UserCreate(UserBase):
    """User model for creation requests"""
    pass


class User(UserBase):
    """Complete User model with all fields"""
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)