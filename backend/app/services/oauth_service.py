# -*- coding: utf-8 -*-
"""
OAuth 2.0 Service
Handles OAuth 2.0/OIDC authentication flows
"""

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.integrations.base_client.errors import OAuthError
from authlib.common.urls import urlparse, extract_params
from typing import Dict, Any, Optional, Tuple
import httpx
import secrets
import logging
from urllib.parse import urlencode, parse_qs
from app.config import settings
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)


class OAuthService:
    """OAuth 2.0 service for third-party authentication"""

    def __init__(self):
        """Initialize OAuth service"""
        self.providers = {
            "google": {
                "client_id": settings.oauth_google_client_id,
                "client_secret": settings.oauth_google_client_secret,
                "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scopes": ["openid", "email", "profile"],
                "issuer": "https://accounts.google.com"
            },
            "github": {
                "client_id": settings.oauth_github_client_id,
                "client_secret": settings.oauth_github_client_secret,
                "authorize_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
                "scopes": ["user:email"],
                "issuer": "https://github.com"
            }
        }

    def is_provider_configured(self, provider: str) -> bool:
        """Check if OAuth provider is configured"""
        if provider not in self.providers:
            return False

        config = self.providers[provider]
        return bool(config["client_id"] and config["client_secret"])

    def generate_authorization_url(
        self,
        provider: str,
        redirect_uri: str,
        state: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL

        Args:
            provider: OAuth provider name
            redirect_uri: Callback URI
            state: Optional state parameter

        Returns:
            Tuple of (authorization_url, state)
        """
        if provider not in self.providers:
            raise ValueError(f"Unsupported OAuth provider: {provider}")

        if not self.is_provider_configured(provider):
            raise ValueError(f"OAuth provider {provider} not configured")

        config = self.providers[provider]

        # Generate state if not provided
        if not state:
            state = secrets.token_urlsafe(32)

        # Store state in Redis for verification
        redis_service.set_cache(
            f"oauth_state:{state}",
            {"provider": provider, "redirect_uri": redirect_uri},
            expires_in=300  # 5 minutes
        )

        # Build authorization URL
        params = {
            "client_id": config["client_id"],
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(config["scopes"]),
            "state": state
        }

        # Add provider-specific parameters
        if provider == "google":
            params["access_type"] = "offline"
            params["prompt"] = "consent"

        authorization_url = f"{config['authorize_url']}?{urlencode(params)}"

        logger.debug(f"Generated OAuth URL for {provider}")
        return authorization_url, state

    async def exchange_code_for_token(
        self,
        provider: str,
        code: str,
        redirect_uri: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            provider: OAuth provider name
            code: Authorization code
            redirect_uri: Callback URI
            state: State parameter

        Returns:
            Token response dictionary
        """
        if provider not in self.providers:
            raise ValueError(f"Unsupported OAuth provider: {provider}")

        if not self.is_provider_configured(provider):
            raise ValueError(f"OAuth provider {provider} not configured")

        # Verify state
        stored_state = redis_service.get_cache(f"oauth_state:{state}")
        if not stored_state or stored_state.get("provider") != provider:
            raise ValueError("Invalid or expired state parameter")

        # Clean up state
        redis_service.delete_cache(f"oauth_state:{state}")

        config = self.providers[provider]

        try:
            async with AsyncOAuth2Client(
                client_id=config["client_id"],
                client_secret=config["client_secret"]
            ) as client:

                token_response = await client.fetch_token(
                    config["token_url"],
                    code=code,
                    redirect_uri=redirect_uri
                )

                logger.debug(f"Token exchange successful for {provider}")
                return token_response

        except OAuthError as e:
            logger.error(f"OAuth token exchange error for {provider}: {e}")
            raise ValueError(f"Token exchange failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during token exchange for {provider}: {e}")
            raise ValueError(f"Token exchange failed: {e}")

    async def get_user_info(
        self,
        provider: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Get user information from OAuth provider

        Args:
            provider: OAuth provider name
            access_token: Access token

        Returns:
            User information dictionary
        """
        if provider not in self.providers:
            raise ValueError(f"Unsupported OAuth provider: {provider}")

        config = self.providers[provider]

        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    config["userinfo_url"],
                    headers=headers
                )

                if response.status_code == 200:
                    user_info = response.json()

                    # Normalize user info across providers
                    normalized_info = self._normalize_user_info(provider, user_info)

                    logger.debug(f"User info retrieved for {provider}")
                    return normalized_info
                else:
                    logger.error(f"Failed to get user info from {provider}: {response.status_code}")
                    raise ValueError(f"Failed to get user info: HTTP {response.status_code}")

        except httpx.RequestError as e:
            logger.error(f"Request error getting user info from {provider}: {e}")
            raise ValueError(f"Failed to get user info: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting user info from {provider}: {e}")
            raise ValueError(f"Failed to get user info: {e}")

    def _normalize_user_info(self, provider: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize user information across different OAuth providers

        Args:
            provider: OAuth provider name
            user_info: Raw user info from provider

        Returns:
            Normalized user information
        """
        if provider == "google":
            return {
                "provider": provider,
                "provider_id": user_info.get("id"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "given_name": user_info.get("given_name"),
                "family_name": user_info.get("family_name"),
                "picture": user_info.get("picture"),
                "verified_email": user_info.get("verified_email", False),
                "locale": user_info.get("locale"),
                "raw": user_info
            }

        elif provider == "github":
            return {
                "provider": provider,
                "provider_id": str(user_info.get("id")),
                "email": user_info.get("email"),
                "name": user_info.get("name") or user_info.get("login"),
                "given_name": None,
                "family_name": None,
                "picture": user_info.get("avatar_url"),
                "verified_email": True,  # GitHub emails are verified
                "locale": None,
                "username": user_info.get("login"),
                "raw": user_info
            }

        else:
            # Generic normalization
            return {
                "provider": provider,
                "provider_id": str(user_info.get("id", user_info.get("sub"))),
                "email": user_info.get("email"),
                "name": user_info.get("name") or user_info.get("preferred_username"),
                "given_name": user_info.get("given_name"),
                "family_name": user_info.get("family_name"),
                "picture": user_info.get("picture") or user_info.get("avatar_url"),
                "verified_email": user_info.get("email_verified", False),
                "locale": user_info.get("locale"),
                "raw": user_info
            }

    async def refresh_oauth_token(
        self,
        provider: str,
        refresh_token: str
    ) -> Dict[str, Any]:
        """
        Refresh OAuth access token

        Args:
            provider: OAuth provider name
            refresh_token: Refresh token

        Returns:
            New token response
        """
        if provider not in self.providers:
            raise ValueError(f"Unsupported OAuth provider: {provider}")

        if not self.is_provider_configured(provider):
            raise ValueError(f"OAuth provider {provider} not configured")

        config = self.providers[provider]

        try:
            async with AsyncOAuth2Client(
                client_id=config["client_id"],
                client_secret=config["client_secret"]
            ) as client:

                token_response = await client.refresh_token(
                    config["token_url"],
                    refresh_token=refresh_token
                )

                logger.debug(f"Token refresh successful for {provider}")
                return token_response

        except OAuthError as e:
            logger.error(f"OAuth token refresh error for {provider}: {e}")
            raise ValueError(f"Token refresh failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during token refresh for {provider}: {e}")
            raise ValueError(f"Token refresh failed: {e}")

    def get_provider_list(self) -> Dict[str, Dict[str, Any]]:
        """
        Get list of configured OAuth providers

        Returns:
            Dictionary of configured providers
        """
        configured_providers = {}

        for name, config in self.providers.items():
            if self.is_provider_configured(name):
                configured_providers[name] = {
                    "name": name,
                    "display_name": name.title(),
                    "scopes": config["scopes"],
                    "issuer": config["issuer"]
                }

        return configured_providers

    async def validate_oauth_token(
        self,
        provider: str,
        access_token: str
    ) -> bool:
        """
        Validate OAuth access token

        Args:
            provider: OAuth provider name
            access_token: Access token to validate

        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Try to get user info with the token
            await self.get_user_info(provider, access_token)
            return True

        except Exception as e:
            logger.debug(f"OAuth token validation failed for {provider}: {e}")
            return False

    def create_pkce_challenge(self) -> Tuple[str, str]:
        """
        Create PKCE code challenge and verifier

        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        import base64
        import hashlib

        # Generate code verifier
        code_verifier = secrets.token_urlsafe(32)

        # Create code challenge
        challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode().rstrip('=')

        return code_verifier, code_challenge


# Global instance
oauth_service = OAuthService()