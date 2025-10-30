"""
Password Utility Functions
Şifre hashing ve doğrulama işlemleri
"""
from passlib.context import CryptContext
import secrets
import string

# Bcrypt context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Şifreyi hash'le

    Args:
        password: Plain text şifre

    Returns:
        Hash'lenmiş şifre
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Şifreyi doğrula

    Args:
        plain_password: Plain text şifre
        hashed_password: Hash'lenmiş şifre

    Returns:
        Şifre doğru ise True, değilse False
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_random_password(length: int = 12) -> str:
    """
    Random güvenli şifre oluştur

    Args:
        length: Şifre uzunluğu (varsayılan 12)

    Returns:
        Random oluşturulmuş güvenli şifre
    """
    # En az bir büyük harf, küçük harf, rakam ve özel karakter içeren şifre
    alphabet = string.ascii_letters + string.digits + string.punctuation

    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))

        # Şifrenin gereksinimleri karşıladığından emin ol
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            return password


def generate_secure_token(length: int = 32) -> str:
    """
    Güvenli random token oluştur (email verification, password reset için)

    Args:
        length: Token uzunluğu (varsayılan 32)

    Returns:
        Güvenli random token
    """
    return secrets.token_urlsafe(length)
