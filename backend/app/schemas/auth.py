"""
Authentication Schemas
Request ve Response modelleri
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


# ==================== REQUEST SCHEMAS ====================

class RegisterRequest(BaseModel):
    """Kullanıcı kayıt isteği"""
    email: EmailStr = Field(..., description="Kullanıcı email adresi")
    password: str = Field(..., min_length=8, description="Kullanıcı şifresi (min 8 karakter)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Kullanıcı adı soyadı")
    username: str = Field(..., min_length=3, max_length=30, description="Kullanıcı adı")

    @validator('username')
    def validate_username(cls, v):
        """Username formatını kontrol et"""
        if not re.match(r'^[a-zA-Z0-9_-]{3,30}$', v):
            raise ValueError('Username sadece harf, rakam, - ve _ içerebilir')
        return v.lower()

    @validator('password')
    def validate_password(cls, v):
        """Şifre güvenlik kontrolü"""
        if len(v) < 8:
            raise ValueError('Şifre en az 8 karakter olmalıdır')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        if not re.search(r'[a-z]', v):
            raise ValueError('Şifre en az bir küçük harf içermelidir')
        if not re.search(r'\d', v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        return v


class LoginRequest(BaseModel):
    """Kullanıcı giriş isteği"""
    email: EmailStr = Field(..., description="Kullanıcı email adresi")
    password: str = Field(..., description="Kullanıcı şifresi")


class VerifyEmailRequest(BaseModel):
    """Email doğrulama isteği"""
    token: str = Field(..., description="Email doğrulama token'ı")


class ResendVerificationRequest(BaseModel):
    """Email doğrulama token'ını tekrar gönderme isteği"""
    email: EmailStr = Field(..., description="Kullanıcı email adresi")


class ForgotPasswordRequest(BaseModel):
    """Şifre sıfırlama talebi"""
    email: EmailStr = Field(..., description="Kullanıcı email adresi")


class ResetPasswordRequest(BaseModel):
    """Şifre sıfırlama isteği"""
    token: str = Field(..., description="Şifre sıfırlama token'ı")
    new_password: str = Field(..., min_length=8, description="Yeni şifre")

    @validator('new_password')
    def validate_password(cls, v):
        """Şifre güvenlik kontrolü"""
        if len(v) < 8:
            raise ValueError('Şifre en az 8 karakter olmalıdır')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        if not re.search(r'[a-z]', v):
            raise ValueError('Şifre en az bir küçük harf içermelidir')
        if not re.search(r'\d', v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        return v


class ChangePasswordRequest(BaseModel):
    """Şifre değiştirme isteği"""
    old_password: str = Field(..., description="Mevcut şifre")
    new_password: str = Field(..., min_length=8, description="Yeni şifre")
    confirm_new_password: str = Field(..., min_length=8, description="Yeni şifre tekrarı")

    @validator('new_password')
    def validate_password(cls, v):
        """Şifre güvenlik kontrolü"""
        if len(v) < 8:
            raise ValueError('Şifre en az 8 karakter olmalıdır')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        if not re.search(r'[a-z]', v):
            raise ValueError('Şifre en az bir küçük harf içermelidir')
        if not re.search(r'\d', v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        return v

    @validator('confirm_new_password')
    def passwords_match(cls, v, values):
        """Şifrelerin eşleştiğini kontrol et"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Yeni şifreler eşleşmiyor')
        return v


class RefreshTokenRequest(BaseModel):
    """Token yenileme isteği"""
    refresh_token: str = Field(..., description="Refresh token")


# ==================== RESPONSE SCHEMAS ====================

class UserResponse(BaseModel):
    """Kullanıcı bilgileri response"""
    id: str
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "user"
    email_verified: bool = False
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    """Authentication response (login/register)"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class MessageResponse(BaseModel):
    """Genel mesaj response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Hata response"""
    error: str
    detail: Optional[str] = None
    success: bool = False


class EmailSentResponse(BaseModel):
    """Email gönderildi response"""
    message: str
    email: str
    success: bool = True
