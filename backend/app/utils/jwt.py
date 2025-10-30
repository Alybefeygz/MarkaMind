"""
JWT Token Utility Functions
JWT token oluşturma ve doğrulama işlemleri
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from uuid import UUID
from app.config import settings


def create_access_token(
    user_id: str | UUID,
    email: str,
    role: str = "user",
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Access token oluştur

    Args:
        user_id: Kullanıcı ID
        email: Kullanıcı email
        role: Kullanıcı rolü
        additional_claims: Ek JWT claims

    Returns:
        JWT access token
    """
    # User ID'yi string'e çevir (UUID ise)
    if isinstance(user_id, UUID):
        user_id = str(user_id)

    # Token expire süresi
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # JWT payload
    payload = {
        "sub": user_id,  # subject (user_id)
        "email": email,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow()
    }

    # Ek claims varsa ekle
    if additional_claims:
        payload.update(additional_claims)

    # JWT token oluştur
    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(
    user_id: str | UUID,
    email: str
) -> str:
    """
    Refresh token oluştur

    Args:
        user_id: Kullanıcı ID
        email: Kullanıcı email

    Returns:
        JWT refresh token
    """
    # User ID'yi string'e çevir (UUID ise)
    if isinstance(user_id, UUID):
        user_id = str(user_id)

    # Token expire süresi (refresh token daha uzun ömürlü)
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    # JWT payload
    payload = {
        "sub": user_id,
        "email": email,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow()
    }

    # JWT token oluştur
    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    JWT token'ı decode et ve doğrula

    Args:
        token: JWT token

    Returns:
        Token payload (dict)

    Raises:
        JWTError: Token geçersiz veya süresi dolmuş
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Token doğrulama hatası: {str(e)}")


def verify_token_type(token: str, expected_type: str) -> Dict[str, Any]:
    """
    Token'ı decode et ve tipini kontrol et

    Args:
        token: JWT token
        expected_type: Beklenen token tipi ("access" veya "refresh")

    Returns:
        Token payload

    Raises:
        JWTError: Token geçersiz veya tip uyuşmuyor
    """
    payload = decode_token(token)

    token_type = payload.get("type")
    if token_type != expected_type:
        raise JWTError(f"Geçersiz token tipi. Beklenen: {expected_type}, Gelen: {token_type}")

    return payload


def get_token_expiry(token: str) -> Optional[datetime]:
    """
    Token'ın expire süresini al

    Args:
        token: JWT token

    Returns:
        Token expire zamanı (datetime)
    """
    try:
        payload = decode_token(token)
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp)
        return None
    except JWTError:
        return None


def is_token_expired(token: str) -> bool:
    """
    Token'ın süresi dolmuş mu kontrol et

    Args:
        token: JWT token

    Returns:
        True: Süresi dolmuş, False: Hala geçerli
    """
    expiry = get_token_expiry(token)
    if not expiry:
        return True

    return datetime.utcnow() > expiry


def extract_user_id(token: str) -> Optional[str]:
    """
    Token'dan user ID'yi çıkar

    Args:
        token: JWT token

    Returns:
        User ID (string)
    """
    try:
        payload = decode_token(token)
        return payload.get("sub")
    except JWTError:
        return None
