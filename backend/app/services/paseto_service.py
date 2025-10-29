# -*- coding: utf-8 -*-
"""
PASETO Token Service
Implements PASETO v4 tokens for enhanced security
"""

import pyseto
from pyseto import Key
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
import json
import secrets
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class PasetoService:
    """PASETO Token service for secure token generation and verification"""

    def __init__(self):
        """Initialize PASETO service with keys"""
        self._private_key = None
        self._public_key = None
        self._symmetric_key = None
        self._keys_initialized = False

    def _setup_keys(self):
        """Setup PASETO keys from environment or generate new ones"""
        try:
            # Try to load keys from environment
            private_key_hex = getattr(settings, 'paseto_private_key', None)
            symmetric_key_hex = getattr(settings, 'paseto_symmetric_key', None)

            if private_key_hex:
                try:
                    # Load existing private key
                    private_key_bytes = bytes.fromhex(private_key_hex)
                    self._private_key = Key.new(version=4, purpose="public", key=private_key_bytes)
                    self._public_key = self._private_key.public_key()
                    logger.info("Loaded PASETO private key from environment")
                except Exception as key_load_error:
                    logger.warning(f"Failed to load private key from environment: {key_load_error}")
                    # Fall back to generating new key
                    self._private_key = None

            if not self._private_key:
                # Generate new asymmetric key pair using nacl
                import nacl.signing
                import nacl.utils

                # Generate Ed25519 private key
                signing_key = nacl.signing.SigningKey.generate()
                private_key_bytes = bytes(signing_key)

                self._private_key = Key.new(version=4, purpose="public", key=private_key_bytes)
                self._public_key = self._private_key.public_key()
                logger.warning("Generated new PASETO private key - save to environment!")
                logger.warning(f"PASETO_PRIVATE_KEY={private_key_bytes.hex()}")

            if symmetric_key_hex:
                try:
                    # Load existing symmetric key
                    symmetric_key_bytes = bytes.fromhex(symmetric_key_hex)
                    self._symmetric_key = Key.new(version=4, purpose="local", key=symmetric_key_bytes)
                    logger.info("Loaded PASETO symmetric key from environment")
                except Exception as key_load_error:
                    logger.warning(f"Failed to load symmetric key from environment: {key_load_error}")
                    # Fall back to generating new key
                    self._symmetric_key = None

            if not self._symmetric_key:
                # Generate new symmetric key
                import nacl.utils
                symmetric_key_bytes = nacl.utils.random(32)  # 256-bit key

                self._symmetric_key = Key.new(version=4, purpose="local", key=symmetric_key_bytes)
                logger.warning("Generated new PASETO symmetric key - save to environment!")
                logger.warning(f"PASETO_SYMMETRIC_KEY={symmetric_key_bytes.hex()}")

        except Exception as e:
            logger.error(f"Failed to setup PASETO keys: {e}")
            # Don't raise exception, allow system to start
            logger.warning("PASETO service will use fallback security")
            self._keys_initialized = False

    def _ensure_keys(self):
        """Ensure keys are initialized (lazy initialization)"""
        if not self._keys_initialized:
            try:
                self._setup_keys()
                self._keys_initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize PASETO keys: {e}")
                # Use fallback - simple secret-based tokens
                return False
        return True

    def _create_fallback_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta], token_type: str) -> str:
        """Create fallback JWT-style token when PASETO fails"""
        import jwt
        from app.config import settings

        if expires_delta is None:
            expires_delta = timedelta(minutes=getattr(settings, 'access_token_expire_minutes', 30))

        now = datetime.now(timezone.utc)
        expire = now + expires_delta

        payload = {
            **data,
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "jti": secrets.token_urlsafe(32),
            "token_type": token_type
        }

        # Use JWT as fallback
        secret = getattr(settings, 'secret_key', 'fallback-secret-key')
        token = jwt.encode(payload, secret, algorithm="HS256")

        logger.warning(f"Using fallback JWT token for {token_type}")
        return token

    def _verify_fallback_token(self, token: str, token_type: str) -> Optional[Dict[str, Any]]:
        """Verify fallback JWT token"""
        try:
            import jwt
            from app.config import settings

            secret = getattr(settings, 'secret_key', 'fallback-secret-key')
            payload = jwt.decode(token, secret, algorithms=["HS256"])

            # Check token type
            if payload.get('token_type') != token_type:
                return None

            # Check expiration
            exp = payload.get('exp')
            if exp and datetime.now(timezone.utc).timestamp() > exp:
                return None

            logger.debug(f"Verified fallback token for {token_type}")
            return payload

        except Exception as e:
            logger.error(f"Failed to verify fallback token: {e}")
            return None

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a PASETO access token (public token - asymmetric)

        Args:
            data: Token payload data
            expires_delta: Token expiration time

        Returns:
            PASETO token string
        """
        try:
            if not self._ensure_keys():
                # Fallback to JWT-style token
                return self._create_fallback_token(data, expires_delta, "access")

            if expires_delta is None:
                expires_delta = timedelta(minutes=getattr(settings, 'access_token_expire_minutes', 30))

            now = datetime.now(timezone.utc)
            expire = now + expires_delta

            # Prepare token payload
            payload = {
                **data,
                "iat": now.isoformat(),
                "exp": expire.isoformat(),
                "nbf": now.isoformat(),
                "jti": secrets.token_urlsafe(32),  # Unique token ID
                "token_type": "access"
            }

            # Create PASETO public token
            token = pyseto.encode(
                key=self._private_key,
                payload=payload,
                footer=b"access_token"
            )

            logger.debug(f"Created access token for: {data.get('sub', 'unknown')}")
            return token.decode('utf-8')

        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            # Fallback to simple token
            return self._create_fallback_token(data, expires_delta, "access")

    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a PASETO refresh token (local token - symmetric encryption)

        Args:
            data: Token payload data
            expires_delta: Token expiration time

        Returns:
            PASETO token string
        """
        try:
            if not self._ensure_keys():
                # Fallback to JWT-style token
                return self._create_fallback_token(data, expires_delta, "refresh")

            if expires_delta is None:
                expires_delta = timedelta(days=getattr(settings, 'refresh_token_expire_days', 30))

            now = datetime.now(timezone.utc)
            expire = now + expires_delta

            # Prepare token payload
            payload = {
                **data,
                "iat": now.isoformat(),
                "exp": expire.isoformat(),
                "nbf": now.isoformat(),
                "jti": secrets.token_urlsafe(32),  # Unique token ID
                "token_type": "refresh"
            }

            # Create PASETO local token (encrypted)
            token = pyseto.encode(
                key=self._symmetric_key,
                payload=payload,
                footer=b"refresh_token"
            )

            logger.debug(f"Created refresh token for: {data.get('sub', 'unknown')}")
            return token.decode('utf-8')

        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            # Fallback to simple token
            return self._create_fallback_token(data, expires_delta, "refresh")

    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a PASETO access token

        Args:
            token: PASETO token string

        Returns:
            Token payload if valid, None otherwise
        """
        try:
            if not self._ensure_keys():
                # Try fallback JWT verification
                return self._verify_fallback_token(token, "access")

            # Decode PASETO public token
            payload = pyseto.decode(
                key=self._public_key,
                token=token.encode('utf-8'),
                expected_footer=b"access_token"
            )

            # Convert payload to dict if it's a string
            if isinstance(payload, (bytes, str)):
                payload = json.loads(payload)

            # Check expiration
            exp_str = payload.get('exp')
            if exp_str:
                exp_time = datetime.fromisoformat(exp_str.replace('Z', '+00:00'))
                if datetime.now(timezone.utc) > exp_time:
                    logger.warning("Access token has expired")
                    return None

            # Check not before
            nbf_str = payload.get('nbf')
            if nbf_str:
                nbf_time = datetime.fromisoformat(nbf_str.replace('Z', '+00:00'))
                if datetime.now(timezone.utc) < nbf_time:
                    logger.warning("Access token not yet valid")
                    return None

            # Check token type
            if payload.get('token_type') != 'access':
                logger.warning("Invalid token type for access token")
                return None

            logger.debug(f"Verified access token for: {payload.get('sub', 'unknown')}")
            return payload

        except Exception as e:
            logger.error(f"Failed to verify access token: {e}")
            # Try fallback verification
            return self._verify_fallback_token(token, "access")

    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a PASETO refresh token

        Args:
            token: PASETO token string

        Returns:
            Token payload if valid, None otherwise
        """
        try:
            # Decode PASETO local token
            payload = pyseto.decode(
                key=self._symmetric_key,
                token=token.encode('utf-8'),
                expected_footer=b"refresh_token"
            )

            # Convert payload to dict if it's a string
            if isinstance(payload, (bytes, str)):
                payload = json.loads(payload)

            # Check expiration
            exp_str = payload.get('exp')
            if exp_str:
                exp_time = datetime.fromisoformat(exp_str.replace('Z', '+00:00'))
                if datetime.now(timezone.utc) > exp_time:
                    logger.warning("Refresh token has expired")
                    return None

            # Check not before
            nbf_str = payload.get('nbf')
            if nbf_str:
                nbf_time = datetime.fromisoformat(nbf_str.replace('Z', '+00:00'))
                if datetime.now(timezone.utc) < nbf_time:
                    logger.warning("Refresh token not yet valid")
                    return None

            # Check token type
            if payload.get('token_type') != 'refresh':
                logger.warning("Invalid token type for refresh token")
                return None

            logger.debug(f"Verified refresh token for: {payload.get('sub', 'unknown')}")
            return payload

        except Exception as e:
            logger.error(f"Failed to verify refresh token: {e}")
            return None

    def get_token_jti(self, token: str, token_type: str = "access") -> Optional[str]:
        """
        Extract JTI (token ID) from token for blacklisting

        Args:
            token: PASETO token string
            token_type: Type of token ("access" or "refresh")

        Returns:
            Token JTI if valid, None otherwise
        """
        try:
            if token_type == "access":
                payload = self.verify_access_token(token)
            else:
                payload = self.verify_refresh_token(token)

            if payload:
                return payload.get('jti')
            return None

        except Exception as e:
            logger.error(f"Failed to extract token JTI: {e}")
            return None

    def create_dpop_token(
        self,
        http_method: str,
        http_uri: str,
        access_token_hash: str,
        nonce: Optional[str] = None
    ) -> str:
        """
        Create a DPoP (Demonstration of Proof-of-Possession) token

        Args:
            http_method: HTTP method (GET, POST, etc.)
            http_uri: Full HTTP URI
            access_token_hash: SHA256 hash of access token
            nonce: Optional nonce from server

        Returns:
            DPoP token string
        """
        try:
            now = datetime.now(timezone.utc)

            # Prepare DPoP payload
            payload = {
                "htm": http_method.upper(),
                "htu": http_uri,
                "iat": now.isoformat(),
                "jti": secrets.token_urlsafe(32),
                "ath": access_token_hash  # Access token hash
            }

            if nonce:
                payload["nonce"] = nonce

            # Create DPoP token
            token = pyseto.encode(
                key=self._private_key,
                payload=payload,
                footer=b"dpop_token"
            )

            logger.debug(f"Created DPoP token for: {http_method} {http_uri}")
            return token.decode('utf-8')

        except Exception as e:
            logger.error(f"Failed to create DPoP token: {e}")
            raise Exception("DPoP token creation failed")

    def verify_dpop_token(
        self,
        token: str,
        http_method: str,
        http_uri: str,
        expected_ath: str,
        max_age_seconds: int = 60
    ) -> bool:
        """
        Verify a DPoP token

        Args:
            token: DPoP token string
            http_method: Expected HTTP method
            http_uri: Expected HTTP URI
            expected_ath: Expected access token hash
            max_age_seconds: Maximum token age in seconds

        Returns:
            True if valid, False otherwise
        """
        try:
            # Decode DPoP token
            payload = pyseto.decode(
                key=self._public_key,
                token=token.encode('utf-8'),
                expected_footer=b"dpop_token"
            )

            # Convert payload to dict if it's a string
            if isinstance(payload, (bytes, str)):
                payload = json.loads(payload)

            # Verify HTTP method
            if payload.get('htm') != http_method.upper():
                logger.warning("DPoP token HTTP method mismatch")
                return False

            # Verify HTTP URI
            if payload.get('htu') != http_uri:
                logger.warning("DPoP token HTTP URI mismatch")
                return False

            # Verify access token hash
            if payload.get('ath') != expected_ath:
                logger.warning("DPoP token access token hash mismatch")
                return False

            # Check age
            iat_str = payload.get('iat')
            if iat_str:
                iat_time = datetime.fromisoformat(iat_str.replace('Z', '+00:00'))
                age = (datetime.now(timezone.utc) - iat_time).total_seconds()
                if age > max_age_seconds:
                    logger.warning("DPoP token too old")
                    return False

            logger.debug("DPoP token verified successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to verify DPoP token: {e}")
            return False

    def get_public_key_jwk(self) -> Dict[str, Any]:
        """
        Get public key in JWK format for DPoP verification

        Returns:
            Public key in JWK format
        """
        try:
            # PASETO v4 uses Ed25519 keys
            public_key_bytes = self._public_key.encode()

            return {
                "kty": "OKP",
                "crv": "Ed25519",
                "x": public_key_bytes.hex(),
                "use": "sig",
                "alg": "EdDSA"
            }

        except Exception as e:
            logger.error(f"Failed to get public key JWK: {e}")
            raise Exception("Public key JWK generation failed")


# Global instance
paseto_service = PasetoService()