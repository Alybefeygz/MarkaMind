from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserResponse(BaseModel):
    """API response schema for User"""
    id: UUID
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: str
    email_verified: bool = False
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = Field(None, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    avatar_url: Optional[str] = None


class UserProfile(BaseModel):
    """Public user profile schema"""
    id: UUID
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: str
    email_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(BaseModel):
    """User model as stored in database (with password_hash)"""
    id: UUID
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    password_hash: str
    role: str
    email_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserStats(BaseModel):
    """User statistics"""
    total_logins: int
    last_login_date: Optional[datetime]
    total_password_resets: int
    account_age_days: int
    is_verified: bool
    total_audit_events: int