# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from app.services.auth_service import AuthService
from app.dependencies import get_current_user, get_current_user_optional
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Pydantic models for request/response
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenRefresh(BaseModel):
    refresh_token: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: Dict[str, Any]

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str
    created_at: Optional[str]
    updated_at: Optional[str]

class MessageResponse(BaseModel):
    message: str
    success: bool = True


# Initialize auth service
auth_service = AuthService()


@router.post("/register", response_model=AuthResponse)
async def register(user_data: UserRegister):
    """
    Register a new user
    """
    try:
        result = await auth_service.register(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        logger.info(f"User registered successfully: {user_data.email}")
        return AuthResponse(**result)
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    """
    Login user and return JWT tokens
    """
    try:
        result = await auth_service.login(
            email=credentials.email,
            password=credentials.password
        )
        
        logger.info(f"User logged in successfully: {credentials.email}")
        return AuthResponse(**result)
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(token_data: TokenRefresh):
    """
    Refresh access token using refresh token
    """
    try:
        result = await auth_service.refresh_token(token_data.refresh_token)
        
        logger.info("Token refreshed successfully")
        return AuthResponse(**result)
        
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user and invalidate session
    """
    try:
        # Get the token from the request (we'll need to extract it)
        # For now, we'll just mark the user as logged out
        user_id = current_user.get("id")
        
        # In a real implementation, you might want to blacklist the token
        # For now, we'll just return success
        logger.info(f"User logged out: {user_id}")
        
        return MessageResponse(
            message="Logged out successfully",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile
    """
    try:
        user_id = current_user.get("id")
        
        # Get full user data from database
        user_data = await auth_service.get_user_by_id(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfile(**user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user profile failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user profile
    """
    try:
        user_id = current_user.get("id")
        
        # Update user profile
        updated_user = await auth_service.update_user_profile(
            user_id=user_id,
            update_data=profile_data.dict(exclude_unset=True)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
            )
        
        logger.info(f"User profile updated: {user_id}")
        return UserProfile(**updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user profile failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password
    """
    try:
        user_id = current_user.get("id")
        
        # Change password
        success = await auth_service.change_password(
            user_id=user_id,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
        
        logger.info(f"Password changed for user: {user_id}")
        return MessageResponse(
            message="Password changed successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.get("/verify-token")
async def verify_token(current_user: dict = Depends(get_current_user_optional)):
    """
    Verify if token is valid (optional endpoint for frontend)
    """
    if current_user:
        return {
            "valid": True,
            "user": {
                "id": current_user.get("id"),
                "email": current_user.get("email"),
                "role": current_user.get("role", "authenticated")
            }
        }
    else:
        return {"valid": False, "user": None}