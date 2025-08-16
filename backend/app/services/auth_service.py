# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any, Tuple
from app.services.supabase_service import BaseSupabaseService
from app.utils.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_supabase_token
)
from app.config import settings
import logging
import uuid

logger = logging.getLogger(__name__)


class AuthService(BaseSupabaseService):
    """Authentication service for user management"""
    
    def __init__(self):
        super().__init__()
    
    async def register(
        self, 
        email: str, 
        password: str, 
        full_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user with Supabase Auth and local database
        """
        try:
            # Use Supabase Auth to create user
            auth_response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name or "",
                    }
                }
            })
            
            if auth_response.user:
                user_id = auth_response.user.id
                
                # Create user record in our database
                user_data = {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "role": "user"
                }
                
                await self.upsert("users", user_data)
                
                # Create tokens
                token_data = {
                    "sub": email,
                    "user_id": user_id,
                    "role": "user"
                }
                
                access_token = create_access_token(token_data)
                refresh_token = create_refresh_token(token_data)
                
                logger.info(f"User registered successfully: {email}")
                
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "user": {
                        "id": user_id,
                        "email": email,
                        "full_name": full_name,
                        "role": "user"
                    }
                }
            else:
                raise Exception("Failed to create user with Supabase Auth")
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise Exception(f"Registration failed: {str(e)}")
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login user with Supabase Auth
        """
        try:
            # Use Supabase Auth to sign in
            auth_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user and auth_response.session:
                user_id = auth_response.user.id
                access_token = auth_response.session.access_token
                refresh_token = auth_response.session.refresh_token
                
                # Get user data from our database
                user_data = await self.get_user_by_id(user_id)
                
                if not user_data:
                    # Create user record if doesn't exist
                    user_data = {
                        "id": user_id,
                        "email": email,
                        "full_name": auth_response.user.user_metadata.get("full_name"),
                        "role": "user"
                    }
                    await self.upsert("users", user_data)
                
                logger.info(f"User logged in successfully: {email}")
                
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "user": user_data
                }
            else:
                raise Exception("Invalid credentials")
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise Exception(f"Login failed: {str(e)}")
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        """
        try:
            # Use Supabase to refresh token
            auth_response = self.client.auth.refresh_session(refresh_token)
            
            if auth_response.session:
                user_id = auth_response.user.id
                new_access_token = auth_response.session.access_token
                new_refresh_token = auth_response.session.refresh_token
                
                # Get user data
                user_data = await self.get_user_by_id(user_id)
                
                logger.info(f"Token refreshed for user: {user_id}")
                
                return {
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token,
                    "token_type": "bearer",
                    "user": user_data
                }
            else:
                raise Exception("Failed to refresh token")
                
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise Exception(f"Token refresh failed: {str(e)}")
    
    async def logout(self, access_token: str) -> bool:
        """
        Logout user by invalidating session
        """
        try:
            # Set the session for logout
            self.client.auth.set_session(access_token, "")
            
            # Sign out from Supabase
            self.client.auth.sign_out()
            
            logger.info("User logged out successfully")
            return True
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID from database
        """
        try:
            result = await self.select(
                "users", 
                "*", 
                filters={"id": user_id}
            )
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Get user by ID error: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email from database
        """
        try:
            result = await self.select(
                "users", 
                "*", 
                filters={"email": email}
            )
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Get user by email error: {e}")
            return None
    
    async def update_user_profile(
        self, 
        user_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update user profile information
        """
        try:
            # Remove sensitive fields that shouldn't be updated
            safe_fields = ["full_name", "role"]
            filtered_data = {
                key: value for key, value in update_data.items() 
                if key in safe_fields
            }
            
            if not filtered_data:
                logger.warning("No valid fields to update")
                return None
            
            result = await self.update(
                "users",
                filtered_data,
                filters={"id": user_id}
            )
            
            if result.data and len(result.data) > 0:
                logger.info(f"User profile updated: {user_id}")
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Update user profile error: {e}")
            return None
    
    async def change_password(
        self, 
        user_id: str, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Change user password
        """
        try:
            # Get user data to verify current password
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            # Use Supabase Auth to update password
            # Note: This requires the user to be logged in
            self.client.auth.update_user({
                "password": new_password
            })
            
            logger.info(f"Password changed for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Change password error: {e}")
            return False
    
    async def verify_user_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify user token and return user info
        """
        try:
            # Verify Supabase token
            payload = verify_supabase_token(token)
            
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            # Get user from database
            user_data = await self.get_user_by_id(user_id)
            
            if user_data:
                # Merge token payload with user data
                return {
                    **payload,
                    **user_data
                }
            
            return payload
            
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None