# -*- coding: utf-8 -*-
"""
DPoP (Demonstration of Proof-of-Possession) Service
Implements DPoP for token binding and replay protection
"""

import hashlib
import json
import secrets
import base64
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
import logging

from app.services.paseto_service import paseto_service
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)


class DPoPService:
    """DPoP service for token binding and replay protection"""

    def __init__(self):
        """Initialize DPoP service"""
        self.max_token_age = 60  # DPoP tokens are valid for 60 seconds
        self.nonce_cache_ttl = 300  # Nonces expire after 5 minutes

    def create_dpop_token(
        self,
        http_method: str,
        http_uri: str,
        access_token: Optional[str] = None,
        nonce: Optional[str] = None
    ) -> str:
        """
        Create a DPoP token

        Args:
            http_method: HTTP method (GET, POST, etc.)
            http_uri: Full HTTP URI being accessed
            access_token: Optional access token to bind
            nonce: Optional server-provided nonce

        Returns:
            DPoP token string
        """
        try:
            # Calculate access token hash if provided
            access_token_hash = None
            if access_token:
                access_token_hash = self._calculate_token_hash(access_token)

            # Use PASETO service to create DPoP token
            dpop_token = paseto_service.create_dpop_token(
                http_method=http_method,
                http_uri=http_uri,
                access_token_hash=access_token_hash or "",
                nonce=nonce
            )

            logger.debug(f"Created DPoP token for {http_method} {http_uri}")
            return dpop_token

        except Exception as e:
            logger.error(f"Failed to create DPoP token: {e}")
            raise Exception("DPoP token creation failed")

    def verify_dpop_token(
        self,
        dpop_token: str,
        http_method: str,
        http_uri: str,
        access_token: Optional[str] = None,
        nonce: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a DPoP token

        Args:
            dpop_token: DPoP token to verify
            http_method: Expected HTTP method
            http_uri: Expected HTTP URI
            access_token: Optional access token to verify binding
            nonce: Optional server nonce to verify

        Returns:
            Verification result dictionary
        """
        try:
            # Calculate expected access token hash
            expected_ath = ""
            if access_token:
                expected_ath = self._calculate_token_hash(access_token)

            # Use PASETO service to verify DPoP token
            is_valid = paseto_service.verify_dpop_token(
                token=dpop_token,
                http_method=http_method,
                http_uri=http_uri,
                expected_ath=expected_ath,
                max_age_seconds=self.max_token_age
            )

            if not is_valid:
                return {
                    "valid": False,
                    "error": "DPoP token verification failed"
                }

            # Extract and validate JTI for replay protection
            jti = self._extract_dpop_jti(dpop_token)
            if not jti:
                return {
                    "valid": False,
                    "error": "DPoP token missing JTI"
                }

            # Check for replay attack
            if self._is_dpop_token_used(jti):
                return {
                    "valid": False,
                    "error": "DPoP token replay detected"
                }

            # Mark token as used
            self._mark_dpop_token_used(jti)

            # Verify nonce if provided
            if nonce and not self._verify_nonce(nonce):
                return {
                    "valid": False,
                    "error": "Invalid or expired nonce"
                }

            logger.debug(f"DPoP token verified successfully for {http_method} {http_uri}")
            return {
                "valid": True,
                "jti": jti,
                "method": http_method,
                "uri": http_uri
            }

        except Exception as e:
            logger.error(f"DPoP token verification error: {e}")
            return {
                "valid": False,
                "error": f"Verification error: {e}"
            }

    def generate_nonce(self, client_id: Optional[str] = None) -> str:
        """
        Generate a server nonce for DPoP

        Args:
            client_id: Optional client identifier

        Returns:
            Base64-encoded nonce string
        """
        try:
            # Generate random nonce
            nonce_bytes = secrets.token_bytes(32)
            nonce = base64.urlsafe_b64encode(nonce_bytes).decode().rstrip('=')

            # Store nonce in cache with expiration
            cache_key = f"dpop_nonce:{nonce}"
            nonce_data = {
                "client_id": client_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            redis_service.set_cache(cache_key, nonce_data, expires_in=self.nonce_cache_ttl)

            logger.debug(f"Generated DPoP nonce: {nonce}")
            return nonce

        except Exception as e:
            logger.error(f"Failed to generate nonce: {e}")
            raise Exception("Nonce generation failed")

    def validate_dpop_binding(
        self,
        access_token: str,
        dpop_token: str,
        http_method: str,
        http_uri: str
    ) -> bool:
        """
        Validate DPoP token binding to access token

        Args:
            access_token: Access token
            dpop_token: DPoP token
            http_method: HTTP method
            http_uri: HTTP URI

        Returns:
            True if binding is valid, False otherwise
        """
        try:
            verification_result = self.verify_dpop_token(
                dpop_token=dpop_token,
                http_method=http_method,
                http_uri=http_uri,
                access_token=access_token
            )

            return verification_result.get("valid", False)

        except Exception as e:
            logger.error(f"DPoP binding validation error: {e}")
            return False

    def _calculate_token_hash(self, token: str) -> str:
        """
        Calculate SHA256 hash of token for DPoP binding

        Args:
            token: Token to hash

        Returns:
            Base64url-encoded hash
        """
        token_bytes = token.encode('utf-8')
        hash_bytes = hashlib.sha256(token_bytes).digest()
        return base64.urlsafe_b64encode(hash_bytes).decode().rstrip('=')

    def _extract_dpop_jti(self, dpop_token: str) -> Optional[str]:
        """
        Extract JTI from DPoP token

        Args:
            dpop_token: DPoP token

        Returns:
            JTI if found, None otherwise
        """
        try:
            # Use PASETO service to decode and extract JTI
            payload = paseto_service.verify_dpop_token(
                token=dpop_token,
                http_method="GET",  # Dummy values for extraction
                http_uri="https://example.com",
                expected_ath="",
                max_age_seconds=86400  # Allow old tokens for JTI extraction
            )

            if payload:
                # This is a simplified extraction - in practice, you'd need to
                # decode the PASETO token to get the actual payload
                # For now, we'll generate a consistent JTI based on token content
                token_hash = hashlib.sha256(dpop_token.encode()).hexdigest()
                return token_hash[:32]

            return None

        except Exception as e:
            logger.error(f"Failed to extract DPoP JTI: {e}")
            return None

    def _is_dpop_token_used(self, jti: str) -> bool:
        """
        Check if DPoP token JTI has been used (replay protection)

        Args:
            jti: Token JTI

        Returns:
            True if token has been used, False otherwise
        """
        try:
            cache_key = f"dpop_used:{jti}"
            used = redis_service.get_cache(cache_key)
            return used is not None

        except Exception as e:
            logger.error(f"Error checking DPoP token usage: {e}")
            return False

    def _mark_dpop_token_used(self, jti: str) -> bool:
        """
        Mark DPoP token JTI as used

        Args:
            jti: Token JTI

        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = f"dpop_used:{jti}"
            used_data = {
                "used_at": datetime.now(timezone.utc).isoformat()
            }

            # Store for longer than max token age to prevent replay
            expires_in = self.max_token_age * 2

            return redis_service.set_cache(cache_key, used_data, expires_in=expires_in)

        except Exception as e:
            logger.error(f"Error marking DPoP token as used: {e}")
            return False

    def _verify_nonce(self, nonce: str) -> bool:
        """
        Verify server-provided nonce

        Args:
            nonce: Nonce to verify

        Returns:
            True if nonce is valid, False otherwise
        """
        try:
            cache_key = f"dpop_nonce:{nonce}"
            nonce_data = redis_service.get_cache(cache_key)

            if not nonce_data:
                logger.warning(f"Invalid or expired nonce: {nonce}")
                return False

            # Remove nonce after use (single-use)
            redis_service.delete_cache(cache_key)

            logger.debug(f"Nonce verified and consumed: {nonce}")
            return True

        except Exception as e:
            logger.error(f"Error verifying nonce: {e}")
            return False

    def create_dpop_proof(
        self,
        access_token: str,
        http_method: str,
        http_uri: str,
        nonce: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create DPoP proof for API requests

        Args:
            access_token: Access token to bind
            http_method: HTTP method
            http_uri: HTTP URI
            nonce: Optional server nonce

        Returns:
            Dictionary with DPoP proof headers
        """
        try:
            # Create DPoP token
            dpop_token = self.create_dpop_token(
                http_method=http_method,
                http_uri=http_uri,
                access_token=access_token,
                nonce=nonce
            )

            # Return headers for HTTP request
            return {
                "Authorization": f"DPoP {access_token}",
                "DPoP": dpop_token
            }

        except Exception as e:
            logger.error(f"Failed to create DPoP proof: {e}")
            raise Exception("DPoP proof creation failed")

    def extract_access_token_from_dpop(self, authorization_header: str) -> Optional[str]:
        """
        Extract access token from DPoP Authorization header

        Args:
            authorization_header: Authorization header value

        Returns:
            Access token if found, None otherwise
        """
        try:
            if not authorization_header.startswith("DPoP "):
                return None

            return authorization_header[5:]  # Remove "DPoP " prefix

        except Exception as e:
            logger.error(f"Error extracting access token from DPoP header: {e}")
            return None

    def validate_dpop_request(
        self,
        authorization_header: str,
        dpop_header: str,
        http_method: str,
        http_uri: str,
        nonce: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate complete DPoP request

        Args:
            authorization_header: Authorization header value
            dpop_header: DPoP header value
            http_method: HTTP method
            http_uri: HTTP URI
            nonce: Optional server nonce

        Returns:
            Validation result dictionary
        """
        try:
            # Extract access token
            access_token = self.extract_access_token_from_dpop(authorization_header)
            if not access_token:
                return {
                    "valid": False,
                    "error": "Invalid Authorization header format"
                }

            # Verify DPoP token
            verification_result = self.verify_dpop_token(
                dpop_token=dpop_header,
                http_method=http_method,
                http_uri=http_uri,
                access_token=access_token,
                nonce=nonce
            )

            if verification_result.get("valid"):
                return {
                    "valid": True,
                    "access_token": access_token,
                    "dpop_jti": verification_result.get("jti")
                }
            else:
                return verification_result

        except Exception as e:
            logger.error(f"DPoP request validation error: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {e}"
            }


# Global instance
dpop_service = DPoPService()