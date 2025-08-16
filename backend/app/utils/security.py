# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    """
    try:
        hashed = pwd_context.hash(password)
        logger.info("Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.info(f"Password verification: {'success' if result else 'failed'}")
        return result
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    """
    try:
        to_encode = data.copy()
        
        # Set expiration time
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        to_encode.update({"iat": datetime.utcnow()})
        
        # Create JWT token
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.secret_key, 
            algorithm=settings.algorithm
        )
        
        logger.info(f"Access token created for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        raise


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token
    """
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            logger.warning("Token has expired")
            return None
        
        logger.info(f"Token verified for user: {payload.get('sub', 'unknown')}")
        return payload
        
    except JWTError as e:
        logger.error(f"JWT verification error: {e}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None


def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Supabase JWT token using Supabase JWT secret
    """
    try:
        # Decode JWT token with Supabase JWT secret
        payload = jwt.decode(
            token, 
            settings.supabase_jwt_secret, 
            algorithms=[settings.algorithm]
        )
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            logger.warning("Supabase token has expired")
            return None
        
        logger.info(f"Supabase token verified for user: {payload.get('sub', 'unknown')}")
        return payload
        
    except JWTError as e:
        logger.error(f"Supabase JWT verification error: {e}")
        return None
    except Exception as e:
        logger.error(f"Supabase token verification error: {e}")
        return None


def create_refresh_token(data: dict) -> str:
    """
    Create a refresh token with longer expiration
    """
    try:
        to_encode = data.copy()
        
        # Refresh token expires in 7 days
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire})
        to_encode.update({"iat": datetime.utcnow()})
        to_encode.update({"token_type": "refresh"})
        
        # Create JWT refresh token
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.secret_key, 
            algorithm=settings.algorithm
        )
        
        logger.info(f"Refresh token created for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Refresh token creation error: {e}")
        raise


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify refresh token
    """
    try:
        payload = verify_token(token)
        
        if not payload:
            return None
        
        # Check if this is a refresh token
        if payload.get("token_type") != "refresh":
            logger.warning("Token is not a refresh token")
            return None
        
        return payload
        
    except Exception as e:
        logger.error(f"Refresh token verification error: {e}")
        return None


def generate_password_reset_token(email: str) -> str:
    """
    Generate password reset token
    """
    try:
        data = {
            "sub": email,
            "token_type": "password_reset"
        }
        
        # Password reset token expires in 1 hour
        expire_delta = timedelta(hours=1)
        return create_access_token(data, expire_delta)
        
    except Exception as e:
        logger.error(f"Password reset token generation error: {e}")
        raise


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token and return email
    """
    try:
        payload = verify_token(token)
        
        if not payload:
            return None
        
        # Check if this is a password reset token
        if payload.get("token_type") != "password_reset":
            logger.warning("Token is not a password reset token")
            return None
        
        email = payload.get("sub")
        if not email:
            logger.warning("Password reset token missing email")
            return None
        
        return email
        
    except Exception as e:
        logger.error(f"Password reset token verification error: {e}")
        return None