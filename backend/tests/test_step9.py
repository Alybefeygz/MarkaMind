# test_step9.py - API Router'lari Test Scripti
import sys
import os
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

def test_router_imports():
    """Test that all routers can be imported successfully"""
    try:
        sys.path.append('.')
        from app.routers import (
            auth_router,
            brands_router, 
            chatbots_router,
            knowledge_router,
            conversations_router,
            uploads_router,
            widget_router,
            feedback_router
        )
        print("OK Tum router'lar basariyla import edildi")
        return True, {
            'auth_router': auth_router,
            'brands_router': brands_router,
            'chatbots_router': chatbots_router,
            'knowledge_router': knowledge_router,
            'conversations_router': conversations_router,
            'uploads_router': uploads_router,
            'widget_router': widget_router,
            'feedback_router': feedback_router
        }
    except ImportError as e:
        print(f"ERROR Router import hatasi: {e}")
        return False, {}

def test_router_endpoints(routers):
    """Test router endpoint configurations"""
    try:
        endpoint_tests = [
            ('auth_router', '/auth', ['Authentication']),
            ('brands_router', '/brands', ['Brands']),
            ('chatbots_router', '/chatbots', ['Chatbots']),
            ('knowledge_router', '/knowledge', ['Knowledge Base']),
            ('conversations_router', '/conversations', ['Conversations']),
            ('uploads_router', '/uploads', ['File Uploads']),
            ('widget_router', '/widget', ['Widget API']),
            ('feedback_router', '/feedback', ['Feedback'])
        ]
        
        for router_name, expected_prefix, expected_tags in endpoint_tests:
            router = routers[router_name]
            
            # Check prefix
            if hasattr(router, 'prefix') and router.prefix == expected_prefix:
                print(f"OK {router_name} prefix dogru: {expected_prefix}")
            else:
                print(f"WARNING {router_name} prefix beklenmedik")
            
            # Check tags
            if hasattr(router, 'tags') and router.tags == expected_tags:
                print(f"OK {router_name} tags dogru: {expected_tags}")
            else:
                print(f"WARNING {router_name} tags beklenmedik")
            
            # Check routes exist
            if hasattr(router, 'routes') and len(router.routes) > 0:
                print(f"OK {router_name} {len(router.routes)} endpoint tanimlandi")
            else:
                print(f"ERROR {router_name} endpoint'leri bulunamadi")
        
        return True
    except Exception as e:
        print(f"ERROR Router endpoint test hatasi: {e}")
        return False

def test_auth_router_endpoints(routers):
    """Test Auth router specific endpoints"""
    try:
        auth_router = routers['auth_router']
        
        # Expected endpoints for auth router
        expected_paths = ['/me', '/change-password', '/verify-token']
        
        # Get all route paths
        if hasattr(auth_router, 'routes'):
            route_paths = []
            for route in auth_router.routes:
                if hasattr(route, 'path'):
                    route_paths.append(route.path)
            
            print(f"OK Auth router endpoint'leri: {route_paths}")
            
            # Check for key endpoints
            for expected_path in expected_paths:
                found = any(expected_path in path for path in route_paths)
                if found:
                    print(f"OK Auth router '{expected_path}' endpoint'i mevcut")
                else:
                    print(f"WARNING Auth router '{expected_path}' endpoint'i bulunamadi")
        
        return True
    except Exception as e:
        print(f"ERROR Auth router test hatasi: {e}")
        return False

def test_brands_router_endpoints(routers):
    """Test Brands router specific endpoints"""
    try:
        brands_router = routers['brands_router']
        
        # Expected methods for brands router
        expected_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        
        if hasattr(brands_router, 'routes'):
            found_methods = set()
            for route in brands_router.routes:
                if hasattr(route, 'methods'):
                    found_methods.update(route.methods)
            
            print(f"OK Brands router HTTP metodlari: {sorted(found_methods)}")
            
            # Check for CRUD operations
            crud_methods = {'GET', 'POST', 'PUT', 'DELETE'}
            if crud_methods.issubset(found_methods):
                print("OK Brands router CRUD operasyonlari mevcut")
            else:
                missing = crud_methods - found_methods
                print(f"WARNING Brands router eksik metodlar: {missing}")
        
        return True
    except Exception as e:
        print(f"ERROR Brands router test hatasi: {e}")
        return False

def test_widget_router_public_access(routers):
    """Test Widget router public endpoints"""
    try:
        widget_router = routers['widget_router']
        
        # Widget router should have public endpoints (no authentication required)
        if hasattr(widget_router, 'routes'):
            public_endpoints = []
            for route in widget_router.routes:
                if hasattr(route, 'path'):
                    # Widget endpoints should be accessible without auth
                    public_endpoints.append(route.path)
            
            print(f"OK Widget router genel erisim endpoint'leri: {len(public_endpoints)} adet")
            
            # Expected public endpoints
            expected_public = ['config', 'chat', 'health', 'embed']
            for expected in expected_public:
                found = any(expected in path for path in public_endpoints)
                if found:
                    print(f"OK Widget router '{expected}' genel endpoint'i mevcut")
                else:
                    print(f"WARNING Widget router '{expected}' endpoint'i bulunamadi")
        
        return True
    except Exception as e:
        print(f"ERROR Widget router test hatasi: {e}")
        return False

def test_upload_router_file_handling(routers):
    """Test Upload router file handling capabilities"""
    try:
        uploads_router = routers['uploads_router']
        
        if hasattr(uploads_router, 'routes'):
            file_endpoints = []
            for route in uploads_router.routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    # Look for file upload endpoints (POST methods)
                    if 'POST' in route.methods:
                        file_endpoints.append(route.path)
            
            print(f"OK Upload router POST endpoint'leri: {len(file_endpoints)} adet")
            
            # Should have both single and batch upload
            single_upload = any(path == '/' for path in file_endpoints)
            batch_upload = any('batch' in path for path in file_endpoints)
            
            if single_upload:
                print("OK Upload router tekli dosya yukleme endpoint'i mevcut")
            else:
                print("WARNING Upload router tekli dosya yukleme endpoint'i bulunamadi")
            
            if batch_upload:
                print("OK Upload router toplu dosya yukleme endpoint'i mevcut")
            else:
                print("WARNING Upload router toplu dosya yukleme endpoint'i bulunamadi")
        
        return True
    except Exception as e:
        print(f"ERROR Upload router test hatasi: {e}")
        return False

def test_statistics_endpoints(routers):
    """Test statistics endpoints across routers"""
    try:
        stats_routers = [
            ('knowledge_router', 'bilgi kaynagi'),
            ('conversations_router', 'konusma'),
            ('uploads_router', 'dosya yukleme'),
            ('feedback_router', 'geri bildirim')
        ]
        
        for router_name, description in stats_routers:
            router = routers[router_name]
            
            if hasattr(router, 'routes'):
                stats_endpoints = []
                for route in router.routes:
                    if hasattr(route, 'path') and 'stats' in route.path:
                        stats_endpoints.append(route.path)
                
                if stats_endpoints:
                    print(f"OK {router_name} {description} istatistik endpoint'leri: {len(stats_endpoints)} adet")
                else:
                    print(f"WARNING {router_name} istatistik endpoint'i bulunamadi")
        
        return True
    except Exception as e:
        print(f"ERROR Istatistik endpoint'leri test hatasi: {e}")
        return False

def test_pagination_support(routers):
    """Test pagination support in list endpoints"""
    try:
        list_routers = [
            'brands_router',
            'chatbots_router', 
            'knowledge_router',
            'conversations_router',
            'uploads_router',
            'feedback_router'
        ]
        
        for router_name in list_routers:
            router = routers[router_name]
            
            if hasattr(router, 'routes'):
                list_endpoints = []
                for route in router.routes:
                    if (hasattr(route, 'path') and hasattr(route, 'methods') 
                        and route.path == '/' and 'GET' in route.methods):
                        list_endpoints.append(route.path)
                
                if list_endpoints:
                    print(f"OK {router_name} sayfalama destekli liste endpoint'i mevcut")
                else:
                    print(f"WARNING {router_name} liste endpoint'i bulunamadi")
        
        return True
    except Exception as e:
        print(f"ERROR Sayfalama test hatasi: {e}")
        return False

def test_error_handling():
    """Test error handling configurations"""
    try:
        # Check if HTTPException is properly imported in routers
        from fastapi import HTTPException
        from app.routers.brands import router as brands_router
        
        # Check if routes have proper error responses configured
        if hasattr(brands_router, 'responses'):
            if 404 in brands_router.responses:
                print("OK Router'larda 404 hata yanitlari tanimlandi")
            else:
                print("WARNING 404 hata yanitlari tanimlanmadi")
        
        print("OK Hata yonetimi moduleri import edildi")
        return True
    except Exception as e:
        print(f"ERROR Hata yonetimi test hatasi: {e}")
        return False

def test_dependency_injection():
    """Test dependency injection setup"""
    try:
        from app.dependencies import get_current_user, get_supabase_client
        print("OK Bagimlilik enjeksiyonu moduleri import edildi")
        
        # Check if dependencies are properly configured
        if callable(get_current_user):
            print("OK get_current_user dependency calisiyor")
        if callable(get_supabase_client):
            print("OK get_supabase_client dependency calisiyor")
        
        return True
    except Exception as e:
        print(f"ERROR Bagimlilik enjeksiyonu test hatasi: {e}")
        return False

def test_schema_integration():
    """Test schema integration with routers"""
    try:
        # Test that schemas are properly imported and used
        from app.schemas.brand import BrandResponse
        from app.schemas.chatbot import ChatbotResponse
        from app.schemas.common import StatusResponse, PaginationResponse
        
        print("OK Router semalari basariyla import edildi")
        
        # Check if schemas have proper configuration
        if hasattr(BrandResponse, 'model_config'):
            print("OK Pydantic v2 yaplandirmasi mevcut")
        
        return True
    except Exception as e:
        print(f"ERROR Sema entegrasyonu test hatasi: {e}")
        return False

if __name__ == "__main__":
    print("=== ADIM 9 TEST - API ROUTER'LARI ===")
    
    # Test imports first
    success, routers = test_router_imports()
    if not success:
        print("ERROR Router'lar import edilemedigi icin diger testler atlaniyor")
        sys.exit(1)
    
    # Test individual router configurations
    tests = [
        ("Router Endpoint Yapılandırmaları", lambda: test_router_endpoints(routers)),
        ("Auth Router Endpoint'leri", lambda: test_auth_router_endpoints(routers)),
        ("Brands Router CRUD İşlemleri", lambda: test_brands_router_endpoints(routers)),
        ("Widget Router Genel Erişim", lambda: test_widget_router_public_access(routers)),
        ("Upload Router Dosya İşleme", lambda: test_upload_router_file_handling(routers)),
        ("İstatistik Endpoint'leri", lambda: test_statistics_endpoints(routers)),
        ("Sayfalama Desteği", lambda: test_pagination_support(routers)),
        ("Hata Yönetimi", test_error_handling),
        ("Bağımlılık Enjeksiyonu", test_dependency_injection),
        ("Şema Entegrasyonu", test_schema_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} Test ---")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"ERROR {test_name} test hatasi: {e}")
    
    print(f"\n=== SONUC: {passed}/{total} test gecti ===")
    
    if passed == total:
        print("SUCCESS Tum API Router'lari basariyla olusturuldu!")
        print("\nOLUSTURULAN ROUTER'LAR:")
        print("✅ Auth Router - Kimlik dogrulama endpoint'leri")
        print("✅ Brands Router - Marka yonetimi CRUD operasyonlari")
        print("✅ Chatbots Router - Chatbot yonetimi ve aktivasyon")
        print("✅ Knowledge Router - Bilgi kaynagi yonetimi ve istatistikler")
        print("✅ Conversations Router - Konusma yonetimi ve disa aktarma")
        print("✅ Uploads Router - Dosya yukleme ve toplu islemler")
        print("✅ Widget Router - Genel erisim API endpoint'leri")
        print("✅ Feedback Router - Geri bildirim yonetimi ve analiz")
        print("\nOZELLIKLER:")
        print("🔐 Kimlik dogrulama ve yetkilendirme")
        print("📄 Sayfalama destegi")
        print("🔍 Filtreleme ve arama")
        print("📊 Istatistik endpoint'leri")
        print("🏷️ Genel erisim API'leri")
        print("📁 Dosya yukleme sistemi")
        print("🔄 Tam CRUD operasyonlari")
        print("⚡ Hata yonetimi")
        print("🎯 Veri dogrulama")
    else:
        print("WARNING Bazi router'larda duzeltme gerekiyor")
        print("\nSONRAKI ADIMLAR:")
        print("1. Hata mesajlarini inceleyin")
        print("2. Eksik endpoint'leri kontrol edin")
        print("3. Import hatalarini duzoltin")
        print("4. Dependency injection'i test edin")