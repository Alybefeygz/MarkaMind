"""
Authentication Router
Authentication ve kullanıcı yönetimi endpoint'leri
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    VerifyEmailRequest,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    RefreshTokenRequest,
    AuthResponse,
    TokenResponse,
    MessageResponse,
    UserResponse
)
from app.schemas.user import UserUpdate, UserProfile, UserStats
from app.services.auth_service import AuthService
from app.services.token_service import TokenService
from app.services.user_service import UserService
from app.middleware.auth_middleware import (
    get_current_user,
    get_current_verified_user
)
from app.middleware.rate_limit_middleware import (
    rate_limit_auth_endpoints,
    rate_limit_by_ip
)

import logging

logger = logging.getLogger(__name__)

# Router instance
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni kullanıcı kaydı",
    dependencies=[Depends(rate_limit_auth_endpoints)]
)
async def register(
    register_data: RegisterRequest,
    request: Request
) -> MessageResponse:
    """
    Yeni kullanıcı kaydı oluştur

    - **email**: Kullanıcı email adresi
    - **password**: Şifre (min 8 karakter, büyük/küçük harf ve rakam içermeli)
    - **full_name**: Ad soyad
    - **username**: Kullanıcı adı (benzersiz)

    Email verification linki gönderilir.
    """
    result = await AuthService.register(register_data)
    return MessageResponse(
        message=result["message"],
        success=True
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Kullanıcı girişi",
    dependencies=[Depends(rate_limit_auth_endpoints)]
)
async def login(
    login_data: LoginRequest,
    request: Request
) -> AuthResponse:
    """
    Kullanıcı girişi yap

    - **email**: Kullanıcı email adresi
    - **password**: Şifre

    Access token ve refresh token döner.
    """
    return await AuthService.login(login_data)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Kullanıcı çıkışı"
)
async def logout(
    current_user: UserResponse = Depends(get_current_user)
) -> MessageResponse:
    """
    Kullanıcı çıkışı yap

    Authentication gerektirir.
    """
    result = await AuthService.logout(str(current_user.id))
    return MessageResponse(
        message=result["message"],
        success=True
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Token yenileme"
)
async def refresh_token(
    refresh_data: RefreshTokenRequest
) -> TokenResponse:
    """
    Refresh token ile yeni access token al

    - **refresh_token**: Refresh token

    Yeni access token ve refresh token döner.
    """
    result = await AuthService.refresh_access_token(refresh_data.refresh_token)
    return TokenResponse(**result)


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Email doğrulama",
    dependencies=[Depends(rate_limit_by_ip)]
)
async def verify_email(
    verify_data: VerifyEmailRequest,
    request: Request
) -> MessageResponse:
    """
    Email adresini doğrula

    - **token**: Email doğrulama token'ı (email'den gelen link)

    Email doğrulandıktan sonra hesap aktif olur.
    """
    result = await TokenService.verify_email_token(verify_data.token)
    return MessageResponse(
        message=result["message"],
        success=True
    )


@router.post(
    "/resend-verification",
    response_model=MessageResponse,
    summary="Doğrulama emaili tekrar gönder",
    dependencies=[Depends(rate_limit_auth_endpoints)]
)
async def resend_verification(
    resend_data: ResendVerificationRequest,
    request: Request
) -> MessageResponse:
    """
    Email doğrulama linkini tekrar gönder

    - **email**: Kullanıcı email adresi

    Yeni doğrulama email'i gönderilir.
    """
    result = await TokenService.resend_verification_email(resend_data.email)
    return MessageResponse(
        message=result["message"],
        success=True
    )


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Şifre sıfırlama talebi",
    dependencies=[Depends(rate_limit_auth_endpoints)]
)
async def forgot_password(
    forgot_data: ForgotPasswordRequest,
    request: Request
) -> MessageResponse:
    """
    Şifre sıfırlama talebi oluştur

    - **email**: Kullanıcı email adresi

    Email adresine şifre sıfırlama linki gönderilir.
    """
    # Kullanıcıyı bul
    user = await UserService.get_user_by_email(forgot_data.email)

    if not user:
        # Güvenlik için kullanıcı bulunamasa bile success döndür
        # (Email enumeration attack'ı önlemek için)
        return MessageResponse(
            message="Eğer bu email adresi kayıtlıysa, şifre sıfırlama linki gönderildi",
            success=True
        )

    # Token oluştur
    token = await TokenService.create_password_reset_token(
        user_id=str(user.id),
        email=user.email
    )

    # Email gönder
    from app.services.email_service import EmailService
    await EmailService.send_password_reset_email(
        email=user.email,
        full_name=user.full_name or "",
        token=token
    )

    return MessageResponse(
        message="Eğer bu email adresi kayıtlıysa, şifre sıfırlama linki gönderildi",
        success=True
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Şifre sıfırlama",
    dependencies=[Depends(rate_limit_auth_endpoints)]
)
async def reset_password(
    reset_data: ResetPasswordRequest,
    request: Request
) -> MessageResponse:
    """
    Şifreyi sıfırla (token ile)

    - **token**: Şifre sıfırlama token'ı (email'den gelen link)
    - **new_password**: Yeni şifre

    Şifre sıfırlanır ve token kullanılmış olarak işaretlenir.
    """
    # Token'ı doğrula
    token_data = await TokenService.verify_password_reset_token(reset_data.token)

    # Şifreyi sıfırla
    result = await UserService.reset_password(
        user_id=token_data['user_id'],
        new_password=reset_data.new_password
    )

    # Token'ı kullanılmış olarak işaretle
    await TokenService.mark_password_reset_token_used(reset_data.token)

    return MessageResponse(
        message=result["message"],
        success=True
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Şifre değiştirme"
)
async def change_password(
    change_data: ChangePasswordRequest,
    current_user: UserResponse = Depends(get_current_user)
) -> MessageResponse:
    """
    Şifreyi değiştir (authenticated)

    - **old_password**: Mevcut şifre
    - **new_password**: Yeni şifre

    Authentication gerektirir.
    """
    result = await UserService.change_password(
        user_id=str(current_user.id),
        old_password=change_data.old_password,
        new_password=change_data.new_password
    )

    return MessageResponse(
        message=result["message"],
        success=True
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Mevcut kullanıcı bilgileri"
)
async def get_me(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Mevcut kullanıcının bilgilerini getir

    Authentication gerektirir.
    """
    return current_user


@router.get(
    "/profile",
    response_model=UserProfile,
    summary="Kullanıcı profili"
)
async def get_profile(
    current_user: UserResponse = Depends(get_current_user)
) -> UserProfile:
    """
    Kullanıcı profilini getir

    Authentication gerektirir.
    """
    return await UserService.get_user_profile(str(current_user.id))


@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Profil güncelleme"
)
async def update_profile(
    update_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Kullanıcı profilini güncelle

    - **full_name**: Ad soyad (opsiyonel)
    - **username**: Kullanıcı adı (opsiyonel)
    - **avatar_url**: Avatar URL (opsiyonel)

    Authentication gerektirir.
    """
    return await UserService.update_user(
        user_id=str(current_user.id),
        update_data=update_data
    )


@router.get(
    "/stats",
    response_model=UserStats,
    summary="Kullanıcı istatistikleri"
)
async def get_stats(
    current_user: UserResponse = Depends(get_current_verified_user)
) -> UserStats:
    """
    Kullanıcı istatistiklerini getir

    - Toplam giriş sayısı
    - Son giriş tarihi
    - Şifre sıfırlama sayısı
    - Hesap yaşı
    - Email doğrulama durumu
    - Toplam audit event sayısı

    Authentication ve email verification gerektirir.
    """
    return await UserService.get_user_stats(str(current_user.id))


@router.get(
    "/health",
    summary="Health check"
)
async def health_check() -> Dict[str, Any]:
    """
    Auth service health check

    Authentication gerektirmez.
    """
    return {
        "status": "healthy",
        "service": "auth",
        "version": "1.0.0"
    }
