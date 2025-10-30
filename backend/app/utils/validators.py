"""
Validation Utility Functions
Input doğrulama ve sanitizasyon işlemleri
"""
import re
from typing import Optional
from email_validator import validate_email as email_validator_validate, EmailNotValidError


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Email adresini doğrula

    Args:
        email: Email adresi

    Returns:
        (is_valid, error_message) tuple
    """
    try:
        # email-validator kütüphanesi ile doğrula
        validation = email_validator_validate(email, check_deliverability=False)
        # Normalize edilmiş email'i al
        normalized_email = validation.normalized
        return True, None
    except EmailNotValidError as e:
        return False, str(e)


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Şifre güvenlik seviyesini kontrol et

    Args:
        password: Şifre

    Returns:
        (is_valid, error_message) tuple
    """
    if len(password) < 8:
        return False, "Şifre en az 8 karakter olmalıdır"

    if not re.search(r'[A-Z]', password):
        return False, "Şifre en az bir büyük harf içermelidir"

    if not re.search(r'[a-z]', password):
        return False, "Şifre en az bir küçük harf içermelidir"

    if not re.search(r'\d', password):
        return False, "Şifre en az bir rakam içermelidir"

    # Opsiyonel: Özel karakter kontrolü
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     return False, "Şifre en az bir özel karakter içermelidir"

    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Username formatını kontrol et

    Args:
        username: Kullanıcı adı

    Returns:
        (is_valid, error_message) tuple
    """
    # Uzunluk kontrolü
    if len(username) < 3:
        return False, "Username en az 3 karakter olmalıdır"

    if len(username) > 30:
        return False, "Username en fazla 30 karakter olabilir"

    # Format kontrolü: sadece harf, rakam, - ve _
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username sadece harf, rakam, tire (-) ve alt çizgi (_) içerebilir"

    # İlk karakter harf olmalı
    if not username[0].isalpha():
        return False, "Username bir harf ile başlamalıdır"

    return True, None


def validate_full_name(full_name: str) -> tuple[bool, Optional[str]]:
    """
    Ad soyad formatını kontrol et

    Args:
        full_name: Ad soyad

    Returns:
        (is_valid, error_message) tuple
    """
    # Uzunluk kontrolü
    if len(full_name) < 2:
        return False, "Ad soyad en az 2 karakter olmalıdır"

    if len(full_name) > 100:
        return False, "Ad soyad en fazla 100 karakter olabilir"

    # Sadece harf, boşluk ve bazı özel karakterler (Türkçe karakterler dahil)
    if not re.match(r'^[a-zA-ZğĞıİöÖüÜşŞçÇ\s\'-]+$', full_name):
        return False, "Ad soyad sadece harf ve boşluk içerebilir"

    return True, None


def sanitize_input(input_str: str, max_length: Optional[int] = None) -> str:
    """
    Input string'i temizle ve güvenli hale getir

    Args:
        input_str: Temizlenecek string
        max_length: Maksimum uzunluk (optional)

    Returns:
        Temizlenmiş string
    """
    # Boşlukları trim et
    sanitized = input_str.strip()

    # Maksimum uzunluk kontrolü
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # Tehlikeli karakterleri escape et (XSS önleme)
    dangerous_chars = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;',
    }

    for char, escaped in dangerous_chars.items():
        sanitized = sanitized.replace(char, escaped)

    return sanitized


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """
    URL formatını kontrol et

    Args:
        url: URL

    Returns:
        (is_valid, error_message) tuple
    """
    # Basit URL regex pattern
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    if url_pattern.match(url):
        return True, None
    else:
        return False, "Geçersiz URL formatı"


def is_safe_redirect_url(url: str, allowed_hosts: list[str]) -> bool:
    """
    Redirect URL'in güvenli olup olmadığını kontrol et (Open Redirect önleme)

    Args:
        url: Kontrol edilecek URL
        allowed_hosts: İzin verilen host listesi

    Returns:
        True: Güvenli, False: Güvenli değil
    """
    # Relative path ise güvenli
    if url.startswith('/') and not url.startswith('//'):
        return True

    # Absolute URL ise host kontrolü yap
    if url.startswith('http://') or url.startswith('https://'):
        for host in allowed_hosts:
            if host in url:
                return True
        return False

    return False
