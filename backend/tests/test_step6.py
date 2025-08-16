# test_step6.py
# -*- coding: utf-8 -*-
import asyncio
import sys
import os
import json
from typing import Dict, Any

async def test_security_utils_import():
    """Test security utils import"""
    try:
        sys.path.insert(0, os.getcwd())
        from app.utils.security import (
            hash_password, 
            verify_password, 
            create_access_token, 
            verify_token,
            create_refresh_token,
            verify_refresh_token,
            verify_supabase_token
        )
        print("[OK] security.py tum fonksiyonlar import edildi")
        return True
    except Exception as e:
        print(f"[FAIL] Security utils import hatasi: {e}")
        return False

async def test_dependencies_import():
    """Test dependencies import"""
    try:
        from app.dependencies import (
            get_current_user, 
            get_current_user_optional, 
            verify_admin_user
        )
        print("[OK] dependencies.py tum fonksiyonlar import edildi")
        return True
    except Exception as e:
        print(f"[FAIL] Dependencies import hatasi: {e}")
        return False

async def test_auth_service_import():
    """Test AuthService import"""
    try:
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        print("[OK] AuthService class'i import edildi ve instance olusturuldu")
        
        # Check required methods exist
        required_methods = [
            'register', 'login', 'refresh_token', 'logout', 
            'get_user_by_id', 'get_user_by_email', 'update_user_profile',
            'change_password', 'verify_user_token'
        ]
        
        for method in required_methods:
            if hasattr(auth_service, method):
                print(f"[OK] AuthService.{method} metodu mevcut")
            else:
                print(f"[FAIL] AuthService.{method} metodu bulunamadi")
        
        return True
    except Exception as e:
        print(f"[FAIL] AuthService import hatasi: {e}")
        return False

async def test_auth_router_import():
    """Test auth router import"""
    try:
        from app.routers.auth import router, auth_service
        print("[OK] auth router import edildi")
        
        # Check if router has routes
        routes = [route.path for route in router.routes]
        expected_routes = [
            "/auth/register", "/auth/login", "/auth/refresh", 
            "/auth/logout", "/auth/me", "/auth/change-password", 
            "/auth/verify-token"
        ]
        
        for route in expected_routes:
            if route in routes:
                print(f"[OK] {route} endpoint'i mevcut")
            else:
                print(f"[FAIL] {route} endpoint'i bulunamadi")
        
        return True
    except Exception as e:
        print(f"[FAIL] Auth router import hatasi: {e}")
        return False

async def test_pydantic_models():
    """Test Pydantic models"""
    try:
        from app.routers.auth import (
            UserRegister, UserLogin, TokenRefresh, 
            UserProfileUpdate, AuthResponse, UserProfile, MessageResponse
        )
        
        # Test UserRegister model
        user_data = UserRegister(
            email="test@example.com",
            password="testpassword123",
            full_name="Test User"
        )
        print("[OK] UserRegister model test edildi")
        
        # Test UserLogin model
        login_data = UserLogin(
            email="test@example.com",
            password="testpassword123"
        )
        print("[OK] UserLogin model test edildi")
        
        # Test response models
        auth_response_data = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "token_type": "bearer",
            "user": {"id": "123", "email": "test@example.com"}
        }
        auth_response = AuthResponse(**auth_response_data)
        print("[OK] AuthResponse model test edildi")
        
        return True
    except Exception as e:
        print(f"[FAIL] Pydantic models test hatasi: {e}")
        return False

async def test_password_hashing():
    """Test password hashing functions"""
    try:
        from app.utils.security import hash_password, verify_password
        
        # Test password hashing
        password = "test_password_123"
        hashed = hash_password(password)
        
        if hashed and len(hashed) > 50:  # bcrypt hashes are typically 60+ chars
            print("[OK] Password hashing calisiyor")
        else:
            print("[FAIL] Password hashing hatali")
            return False
        
        # Test password verification
        if verify_password(password, hashed):
            print("[OK] Password verification calisiyor")
        else:
            print("[FAIL] Password verification hatali")
            return False
        
        # Test wrong password
        if not verify_password("wrong_password", hashed):
            print("[OK] Yanlis password dogrulama calisiyor")
        else:
            print("[FAIL] Yanlis password kabul edildi")
            return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Password hashing test hatasi: {e}")
        return False

async def test_jwt_tokens():
    """Test JWT token creation and verification"""
    try:
        from app.utils.security import create_access_token, verify_token, create_refresh_token
        
        # Test access token
        test_data = {
            "sub": "test@example.com",
            "user_id": "123",
            "role": "user"
        }
        
        access_token = create_access_token(test_data)
        if access_token and len(access_token) > 100:  # JWT tokens are quite long
            print("[OK] Access token olusturuldu")
        else:
            print("[FAIL] Access token olusturulamadi")
            return False
        
        # Test token verification
        payload = verify_token(access_token)
        if payload and payload.get("sub") == "test@example.com":
            print("[OK] Access token dogrulandi")
        else:
            print("[FAIL] Access token dogrulanamadi")
            return False
        
        # Test refresh token
        refresh_token = create_refresh_token(test_data)
        if refresh_token and len(refresh_token) > 100:
            print("[OK] Refresh token olusturuldu")
        else:
            print("[FAIL] Refresh token olusturulamadi")
            return False
        
        return True
    except Exception as e:
        print(f"[FAIL] JWT token test hatasi: {e}")
        return False

async def test_main_app_with_auth():
    """Test if main app includes auth router"""
    try:
        from app.main import app
        
        # Check if auth routes are included
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
            elif hasattr(route, 'routes'):  # APIRouter
                for sub_route in route.routes:
                    if hasattr(sub_route, 'path'):
                        routes.append(sub_route.path)
        
        auth_routes_found = any("/auth/" in route for route in routes)
        
        if auth_routes_found:
            print("[OK] Auth router main app'e eklendi")
        else:
            print("[FAIL] Auth router main app'e eklenmedi")
            return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Main app auth router test hatasi: {e}")
        return False

async def test_environment_setup():
    """Test environment configuration for auth"""
    try:
        from app.config import settings
        
        # Check required auth settings
        auth_configs = [
            ("SECRET_KEY", settings.secret_key),
            ("ALGORITHM", settings.algorithm),
            ("ACCESS_TOKEN_EXPIRE_MINUTES", settings.access_token_expire_minutes),
            ("SUPABASE_JWT_SECRET", settings.supabase_jwt_secret)
        ]
        
        for config_name, config_value in auth_configs:
            if config_value:
                print(f"[OK] {config_name} environment'da mevcut")
            else:
                print(f"[FAIL] {config_name} environment'da bulunamadi")
        
        return True
    except Exception as e:
        print(f"[FAIL] Environment setup test hatasi: {e}")
        return False

async def test_integration():
    """Test basic integration"""
    try:
        from app.services.auth_service import AuthService
        from app.utils.security import hash_password
        
        # Create auth service instance
        auth_service = AuthService()
        
        # Test that service can be created without errors
        print("[OK] AuthService integration test basarili")
        
        # Test password security integration
        test_password = "integration_test_123"
        hashed = hash_password(test_password)
        
        if hashed:
            print("[OK] Security utils integration test basarili")
        
        return True
    except Exception as e:
        print(f"[FAIL] Integration test hatasi: {e}")
        return False

async def main():
    print("=== ADIM 6 TEST: AUTHENTICATION SYSTEM ===")
    print("Authentication sistemi test ediliyor...\n")
    
    tests = [
        ("Security Utils Import", test_security_utils_import),
        ("Dependencies Import", test_dependencies_import),
        ("Auth Service Import", test_auth_service_import),
        ("Auth Router Import", test_auth_router_import),
        ("Pydantic Models", test_pydantic_models),
        ("Password Hashing", test_password_hashing),
        ("JWT Tokens", test_jwt_tokens),
        ("Main App Integration", test_main_app_with_auth),
        ("Environment Setup", test_environment_setup),
        ("Integration Test", test_integration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"[SUCCESS] {test_name} BASARILI")
            else:
                failed += 1
                print(f"[FAIL] {test_name} BASARISIZ")
        except Exception as e:
            failed += 1
            print(f"[ERROR] {test_name} HATA: {e}")
    
    print(f"\n=== TEST SONUÇLARI ===")
    print(f"Başarılı: {passed}")
    print(f"Başarısız: {failed}")
    print(f"Toplam: {passed + failed}")
    
    if failed == 0:
        print("\n[SUCCESS] TUM TESTLER BASARILI! Step 6 tamamlandi.")
        print("\nSONRAKI ADIM: Step 7 - Pydantic Models ve Schemas")
    else:
        print(f"\n[WARNING] {failed} test basarisiz. Hatalari duzeltin.")

if __name__ == "__main__":
    asyncio.run(main())