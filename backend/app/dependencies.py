# -*- coding: utf-8 -*-
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from app.config import settings
from app.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer scheme for token authentication
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Get current user from JWT token
    Validates Supabase JWT token and returns user info
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Decode JWT token with Supabase JWT secret
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            audience="authenticated"
        )
        
        # Extract user info from token
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            logger.warning("Token missing required fields")
            raise credentials_exception
            
        # Create user info dict
        user_info = {
            "id": user_id,
            "email": email,
            "aud": payload.get("aud"),
            "role": payload.get("role", "authenticated"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }
        
        logger.info(f"User authenticated: {email}")
        return user_info
        
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise credentials_exception


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    Get current user from JWT token (optional)
    Returns None if no token provided or token is invalid
    """
    if credentials is None:
        return None
    
    try:
        # Use the main get_current_user function but catch exceptions
        from fastapi.security import HTTPAuthorizationCredentials
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=credentials.credentials
        )
        return get_current_user(mock_credentials)
    except HTTPException:
        return None
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
        return None


async def get_user_from_db(user_id: str) -> Optional[dict]:
    """
    Get full user info from database
    """
    try:
        client = get_supabase_client()
        result = client.table('users').select('*').eq('id', user_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
        
    except Exception as e:
        logger.error(f"Database user fetch error: {e}")
        return None


def get_current_user_with_db(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get current user with full database info
    """
    try:
        # Get user from database
        import asyncio
        user_data = asyncio.create_task(get_user_from_db(current_user["id"]))
        db_user = asyncio.run(user_data)
        
        if db_user:
            # Merge JWT user info with database info
            return {**current_user, **db_user}
        else:
            # Return just JWT info if database user not found
            logger.warning(f"User {current_user['id']} not found in database")
            return current_user
            
    except Exception as e:
        logger.error(f"User database lookup error: {e}")
        return current_user


def verify_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Verify that current user is admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user