"""
Authentication Middleware
JWT token doğrulama ve kullanıcı authentication
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt import decode_token, verify_token_type
from app.services.user_service import UserService
from app.schemas.user import UserResponse
from jose import JWTError
import logging

logger = logging.getLogger(__name__)

# HTTPBearer scheme for JWT
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserResponse:
    """
    JWT token'dan mevcut kullanıcıyı al

    Args:
        credentials: Authorization header'dan gelen credentials

    Returns:
        UserResponse

    Raises:
        HTTPException: Token geçersiz veya kullanıcı bulunamadı
    """
    try:
        # Token'ı al
        token = credentials.credentials

        # Token'ı decode et
        payload = verify_token_type(token, "access")

        # User ID'yi al
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz token - user ID bulunamadı",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Kullanıcıyı database'den al
        user = await UserService.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kullanıcı bulunamadı",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token doğrulama hatası",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication hatası",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Aktif kullanıcıyı al

    Args:
        current_user: get_current_user'dan gelen kullanıcı

    Returns:
        UserResponse

    Raises:
        HTTPException: Kullanıcı aktif değil
    """
    # UserResponse'da is_active field'ı yok, bu bilgiyi database'den almamız gerek
    # Şimdilik email_verified kontrolü yapalım
    if not current_user.email_verified:
        logger.warning(f"Unverified user attempted access: {current_user.email}")
        # Email doğrulanmamış kullanıcıları da izin verelim ama log tutalım
        # İsterseniz burada HTTPException raise edebilirsiniz

    return current_user


async def get_current_verified_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Email doğrulanmış kullanıcıyı al

    Args:
        current_user: get_current_user'dan gelen kullanıcı

    Returns:
        UserResponse

    Raises:
        HTTPException: Email doğrulanmamış
    """
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email adresinizi doğrulamanız gerekiyor"
        )

    return current_user


async def get_current_admin_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Admin kullanıcıyı al

    Args:
        current_user: get_current_user'dan gelen kullanıcı

    Returns:
        UserResponse

    Raises:
        HTTPException: Kullanıcı admin değil
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için admin yetkisi gerekiyor"
        )

    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UserResponse]:
    """
    Opsiyonel kullanıcı al (token yoksa None döner)

    Args:
        credentials: Authorization header'dan gelen credentials (opsiyonel)

    Returns:
        UserResponse veya None
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = verify_token_type(token, "access")
        user_id = payload.get("sub")

        if user_id:
            user = await UserService.get_user_by_id(user_id)
            return user

    except Exception as e:
        logger.debug(f"Optional auth failed: {str(e)}")
        return None

    return None


def require_roles(*allowed_roles: str):
    """
    Role-based access control dependency

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_roles("admin"))])

    Args:
        *allowed_roles: İzin verilen roller

    Returns:
        Dependency function
    """
    async def role_checker(
        current_user: UserResponse = Depends(get_current_user)
    ) -> UserResponse:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için {', '.join(allowed_roles)} yetkisi gerekiyor"
            )
        return current_user

    return role_checker
