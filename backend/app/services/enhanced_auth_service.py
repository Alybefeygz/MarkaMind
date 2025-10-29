# -*- coding: utf-8 -*-
"""
Enhanced Authentication Service
Combines PASETO + OAuth + DPoP for modern authentication
"""

from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta
import logging
import hashlib
import secrets

from app.services.supabase_service import BaseSupabaseService
from app.services.paseto_service import paseto_service
from app.services.oauth_service import oauth_service
from app.services.dpop_service import dpop_service
from app.services.redis_service import redis_service
from app.utils.security import hash_password, verify_password
from app.config import settings

logger = logging.getLogger(__name__)


class EnhancedAuthService(BaseSupabaseService):
    """Enhanced authentication service with PASETO + OAuth + DPoP"""

    def __init__(self):
        super().__init__()

    async def register(
        self,
        email: str,
        password: str,
        username: str,
        full_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user with enhanced security

        Args:
            email: User email
            password: User password
            username: Unique username
            full_name: Optional full name

        Returns:
            Registration result with PASETO tokens
        """
        try:
            # Check if user already exists by email
            existing_user = await self.get_user_by_email(email)
            if existing_user:
                raise Exception("User already exists")

            # Check if username is already taken
            existing_username = await self.get_user_by_username(username)
            if existing_username:
                raise Exception("Username already taken")

            # Use Supabase Auth for user creation
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
                    "username": username,
                    "full_name": full_name,
                    "role": "user",
                    "auth_method": "password",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }

                await self.upsert("users", user_data)

                # Create PASETO tokens
                token_data = {
                    "sub": email,
                    "user_id": user_id,
                    "role": "user",
                    "auth_method": "password"
                }

                access_token = paseto_service.create_access_token(token_data)
                refresh_token = paseto_service.create_refresh_token(token_data)

                logger.info(f"User registered successfully with PASETO: {email}")

                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "DPoP",
                    "expires_in": settings.access_token_expire_minutes * 60,
                    "user": {
                        "id": user_id,
                        "email": email,
                        "full_name": full_name,
                        "role": "user",
                        "auth_method": "password"
                    }
                }
            else:
                raise Exception("Failed to create user with Supabase Auth")

        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise Exception(f"Registration failed: {str(e)}")

    async def login(
        self,
        email: str,
        password: str,
        client_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Login user with enhanced security

        Args:
            email: User email
            password: User password
            client_info: Optional client information

        Returns:
            Login result with PASETO tokens
        """
        try:
            # Use Supabase Auth for authentication
            auth_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if auth_response.user and auth_response.session:
                user_id = auth_response.user.id

                # Get user data from our database
                user_data = await self.get_user_by_id(user_id)

                if not user_data:
                    # Create user record if doesn't exist
                    user_data = {
                        "id": user_id,
                        "email": email,
                        "full_name": auth_response.user.user_metadata.get("full_name"),
                        "role": "user",
                        "auth_method": "password",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    await self.upsert("users", user_data)

                # Update last login
                await self.update(
                    "users",
                    {"last_login": datetime.now(timezone.utc).isoformat()},
                    filters={"id": user_id}
                )

                # Create PASETO tokens
                token_data = {
                    "sub": email,
                    "user_id": user_id,
                    "role": user_data.get("role", "user"),
                    "auth_method": "password"
                }

                # Add client info if provided
                if client_info:
                    token_data["client_info"] = client_info

                access_token = paseto_service.create_access_token(token_data)
                refresh_token = paseto_service.create_refresh_token(token_data)

                logger.info(f"User logged in successfully with PASETO: {email}")

                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "DPoP",
                    "expires_in": settings.access_token_expire_minutes * 60,
                    "user": user_data
                }
            else:
                raise Exception("Invalid credentials")

        except Exception as e:
            logger.error(f"Login error: {e}")
            raise Exception(f"Login failed: {str(e)}")

    async def oauth_login(
        self,
        provider: str,
        code: str,
        redirect_uri: str,
        state: str
    ) -> Dict[str, Any]:
        """
        OAuth login flow

        Args:
            provider: OAuth provider name
            code: Authorization code
            redirect_uri: Redirect URI
            state: State parameter

        Returns:
            Login result with PASETO tokens
        """
        try:
            # Exchange code for token
            token_response = await oauth_service.exchange_code_for_token(
                provider=provider,
                code=code,
                redirect_uri=redirect_uri,
                state=state
            )

            # Get user info from provider
            user_info = await oauth_service.get_user_info(
                provider=provider,
                access_token=token_response["access_token"]
            )

            if not user_info.get("email"):
                raise Exception("No email provided by OAuth provider")

            email = user_info["email"]
            provider_id = user_info["provider_id"]

            # Check if user exists
            user_data = await self.get_user_by_email(email)

            if not user_data:
                # Create new user
                user_id = f"oauth_{provider}_{provider_id}_{secrets.token_hex(8)}"
                user_data = {
                    "id": user_id,
                    "email": email,
                    "full_name": user_info.get("name"),
                    "role": "user",
                    "auth_method": f"oauth_{provider}",
                    "oauth_provider": provider,
                    "oauth_provider_id": provider_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                await self.upsert("users", user_data)
                logger.info(f"Created new OAuth user: {email} via {provider}")
            else:
                # Update existing user OAuth info
                user_id = user_data["id"]
                await self.update(
                    "users",
                    {
                        "oauth_provider": provider,
                        "oauth_provider_id": provider_id,
                        "last_login": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    },
                    filters={"id": user_id}
                )
                user_data = await self.get_user_by_id(user_id)

            # Create PASETO tokens
            token_data = {
                "sub": email,
                "user_id": user_id,
                "role": user_data.get("role", "user"),
                "auth_method": f"oauth_{provider}",
                "oauth_provider": provider
            }

            access_token = paseto_service.create_access_token(token_data)
            refresh_token = paseto_service.create_refresh_token(token_data)

            logger.info(f"OAuth login successful: {email} via {provider}")

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "DPoP",
                "expires_in": settings.access_token_expire_minutes * 60,
                "user": user_data,
                "oauth_info": user_info
            }

        except Exception as e:
            logger.error(f"OAuth login error for {provider}: {e}")
            raise Exception(f"OAuth login failed: {str(e)}")

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using PASETO refresh token

        Args:
            refresh_token: PASETO refresh token

        Returns:
            New token pair
        """
        try:
            # Verify refresh token
            payload = paseto_service.verify_refresh_token(refresh_token)
            if not payload:
                raise Exception("Invalid refresh token")

            # Check if token is blacklisted
            jti = payload.get('jti')
            if jti and redis_service.is_token_blacklisted(jti):
                raise Exception("Refresh token has been revoked")

            user_id = payload.get("user_id")
            if not user_id:
                raise Exception("Invalid token payload")

            # Get current user data
            user_data = await self.get_user_by_id(user_id)
            if not user_data:
                raise Exception("User not found")

            # Create new tokens
            token_data = {
                "sub": payload.get("sub"),
                "user_id": user_id,
                "role": user_data.get("role", "user"),
                "auth_method": payload.get("auth_method", "password")
            }

            # Add OAuth info if present
            if payload.get("oauth_provider"):
                token_data["oauth_provider"] = payload.get("oauth_provider")

            new_access_token = paseto_service.create_access_token(token_data)
            new_refresh_token = paseto_service.create_refresh_token(token_data)

            # Blacklist old refresh token
            if jti:
                # Calculate remaining TTL for the old token
                exp_str = payload.get('exp')
                if exp_str:
                    exp_time = datetime.fromisoformat(exp_str.replace('Z', '+00:00'))
                    remaining_seconds = int((exp_time - datetime.now(timezone.utc)).total_seconds())
                    if remaining_seconds > 0:
                        redis_service.blacklist_token(jti, remaining_seconds)

            logger.info(f"Token refreshed for user: {user_id}")

            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "DPoP",
                "expires_in": settings.access_token_expire_minutes * 60,
                "user": user_data
            }

        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise Exception(f"Token refresh failed: {str(e)}")

    async def logout(self, access_token: str, refresh_token: Optional[str] = None) -> bool:
        """
        Logout user by blacklisting tokens

        Args:
            access_token: Access token to blacklist
            refresh_token: Optional refresh token to blacklist

        Returns:
            True if successful
        """
        try:
            success = True

            # Blacklist access token
            access_jti = paseto_service.get_token_jti(access_token, "access")
            if access_jti:
                # Calculate remaining TTL
                payload = paseto_service.verify_access_token(access_token)
                if payload:
                    exp_str = payload.get('exp')
                    if exp_str:
                        exp_time = datetime.fromisoformat(exp_str.replace('Z', '+00:00'))
                        remaining_seconds = int((exp_time - datetime.now(timezone.utc)).total_seconds())
                        if remaining_seconds > 0:
                            if not redis_service.blacklist_token(access_jti, remaining_seconds):
                                success = False

            # Blacklist refresh token
            if refresh_token:
                refresh_jti = paseto_service.get_token_jti(refresh_token, "refresh")
                if refresh_jti:
                    payload = paseto_service.verify_refresh_token(refresh_token)
                    if payload:
                        exp_str = payload.get('exp')
                        if exp_str:
                            exp_time = datetime.fromisoformat(exp_str.replace('Z', '+00:00'))
                            remaining_seconds = int((exp_time - datetime.now(timezone.utc)).total_seconds())
                            if remaining_seconds > 0:
                                if not redis_service.blacklist_token(refresh_jti, remaining_seconds):
                                    success = False

            if success:
                logger.info("User logged out successfully")
            else:
                logger.warning("Logout completed with some errors")

            return success

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False

    async def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify PASETO token

        Args:
            token: PASETO token
            token_type: Token type ("access" or "refresh")

        Returns:
            Token payload if valid, None otherwise
        """
        try:
            # Verify token based on type
            if token_type == "access":
                payload = paseto_service.verify_access_token(token)
            else:
                payload = paseto_service.verify_refresh_token(token)

            if not payload:
                return None

            # Check if token is blacklisted
            jti = payload.get('jti')
            if jti and redis_service.is_token_blacklisted(jti):
                logger.warning(f"Blacklisted token used: {jti}")
                return None

            # Get current user data
            user_id = payload.get("user_id")
            if user_id:
                user_data = await self.get_user_by_id(user_id)
                if user_data:
                    payload["user"] = user_data

            return payload

        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from database"""
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
        """Get user by email from database"""
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

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username from database"""
        try:
            result = await self.select(
                "users",
                "*",
                filters={"username": username}
            )

            if result.data and len(result.data) > 0:
                return result.data[0]
            return None

        except Exception as e:
            logger.error(f"Get user by username error: {e}")
            return None

    def create_dpop_nonce(self, client_id: Optional[str] = None) -> str:
        """Create DPoP nonce"""
        return dpop_service.generate_nonce(client_id)

    def validate_dpop_request(
        self,
        authorization_header: str,
        dpop_header: str,
        http_method: str,
        http_uri: str,
        nonce: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate DPoP request"""
        return dpop_service.validate_dpop_request(
            authorization_header=authorization_header,
            dpop_header=dpop_header,
            http_method=http_method,
            http_uri=http_uri,
            nonce=nonce
        )

    def get_oauth_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get configured OAuth providers"""
        return oauth_service.get_provider_list()

    def generate_oauth_url(
        self,
        provider: str,
        redirect_uri: str,
        state: Optional[str] = None
    ) -> Tuple[str, str]:
        """Generate OAuth authorization URL"""
        return oauth_service.generate_authorization_url(
            provider=provider,
            redirect_uri=redirect_uri,
            state=state
        )


# Global instance
enhanced_auth_service = EnhancedAuthService()