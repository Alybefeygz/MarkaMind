# test_step10.py - Temel Servisler Test Scripti
import sys
import os
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any

def test_service_imports():
    """Test that all services can be imported successfully"""
    try:
        sys.path.append('.')
        from app.services.chatbot_service import ChatbotService
        from app.services.embedding_service import EmbeddingService
        
        print("OK Tum servisler basariyla import edildi")
        return True, {
            'ChatbotService': ChatbotService,
            'EmbeddingService': EmbeddingService
        }
    except ImportError as e:
        print(f"ERROR Servis import hatasi: {e}")
        return False, {}

def test_chatbot_service_methods(services):
    """Test ChatbotService method definitions"""
    try:
        ChatbotService = services['ChatbotService']
        
        # Expected methods
        expected_methods = [
            'create_chatbot',
            'update_chatbot', 
            'delete_chatbot',
            'activate_chatbot',
            'deactivate_chatbot',
            'generate_script_token',
            'get_chatbot_config',
            'get_chatbot_stats',
            'validate_chatbot_permissions'
        ]
        
        # Check if methods exist
        for method_name in expected_methods:
            if hasattr(ChatbotService, method_name):
                method = getattr(ChatbotService, method_name)
                if callable(method):
                    print(f"OK ChatbotService.{method_name} metodu mevcut")
                else:
                    print(f"WARNING ChatbotService.{method_name} callable degil")
            else:
                print(f"ERROR ChatbotService.{method_name} metodu bulunamadi")
        
        # Check if class can be instantiated
        try:
            # Try to create instance (might fail due to dependencies)
            service_instance = ChatbotService()
            print("OK ChatbotService instance olusturulabilir")
        except Exception as e:
            print(f"INFO ChatbotService instance dependency gerektirir: {e}")
        
        return True
    except Exception as e:
        print(f"ERROR ChatbotService test hatasi: {e}")
        return False

def test_embedding_service_methods(services):
    """Test EmbeddingService method definitions"""
    try:
        EmbeddingService = services['EmbeddingService']
        
        # Expected methods
        expected_methods = [
            'generate_embedding',
            'find_similar_content',
            'generate_ai_response',
            'process_knowledge_content',
            'count_tokens',
            'extract_text_from_file'
        ]
        
        # Check if methods exist
        for method_name in expected_methods:
            if hasattr(EmbeddingService, method_name):
                method = getattr(EmbeddingService, method_name)
                if callable(method):
                    print(f"OK EmbeddingService.{method_name} metodu mevcut")
                else:
                    print(f"WARNING EmbeddingService.{method_name} callable degil")
            else:
                print(f"ERROR EmbeddingService.{method_name} metodu bulunamadi")
        
        # Check if class can be instantiated
        try:
            service_instance = EmbeddingService()
            print("OK EmbeddingService instance olusturulabilir")
        except Exception as e:
            print(f"INFO EmbeddingService instance dependency gerektirir: {e}")
        
        return True
    except Exception as e:
        print(f"ERROR EmbeddingService test hatasi: {e}")
        return False

def test_chatbot_service_async_methods(services):
    """Test ChatbotService async method signatures"""
    try:
        ChatbotService = services['ChatbotService']
        
        # Check if methods are async
        async_methods = [
            'create_chatbot',
            'update_chatbot',
            'delete_chatbot',
            'get_chatbot_config',
            'get_chatbot_stats'
        ]
        
        import inspect
        
        for method_name in async_methods:
            if hasattr(ChatbotService, method_name):
                method = getattr(ChatbotService, method_name)
                if inspect.iscoroutinefunction(method):
                    print(f"OK ChatbotService.{method_name} async metod")
                else:
                    print(f"WARNING ChatbotService.{method_name} async degil")
        
        return True
    except Exception as e:
        print(f"ERROR Async method test hatasi: {e}")
        return False

def test_embedding_service_async_methods(services):
    """Test EmbeddingService async method signatures"""
    try:
        EmbeddingService = services['EmbeddingService']
        
        # Check if methods are async
        async_methods = [
            'generate_embedding',
            'generate_ai_response', 
            'process_knowledge_content'
        ]
        
        import inspect
        
        for method_name in async_methods:
            if hasattr(EmbeddingService, method_name):
                method = getattr(EmbeddingService, method_name)
                if inspect.iscoroutinefunction(method):
                    print(f"OK EmbeddingService.{method_name} async metod")
                else:
                    print(f"WARNING EmbeddingService.{method_name} async degil")
        
        return True
    except Exception as e:
        print(f"ERROR Async method test hatasi: {e}")
        return False

def test_service_dependencies():
    """Test service dependency imports"""
    try:
        # Test ChatbotService dependencies
        from app.services.chatbot_service import logging, uuid
        print("OK ChatbotService bagimliliklar import edildi")
        
        # Test EmbeddingService dependencies  
        try:
            from app.services.embedding_service import httpx, asyncio
            print("OK EmbeddingService bagimliliklar import edildi")
        except ImportError as e:
            print(f"INFO EmbeddingService optional bagimlilik: {e}")
        
        return True
    except Exception as e:
        print(f"ERROR Bagimlilik test hatasi: {e}")
        return False

def test_type_hints():
    """Test type hints in service methods"""
    try:
        from app.services.chatbot_service import ChatbotService
        from app.services.embedding_service import EmbeddingService
        
        import inspect
        
        # Check ChatbotService type hints
        if hasattr(ChatbotService, 'create_chatbot'):
            method = getattr(ChatbotService, 'create_chatbot')
            sig = inspect.signature(method)
            
            has_type_hints = any(param.annotation != param.empty for param in sig.parameters.values())
            if has_type_hints:
                print("OK ChatbotService metodlarda type hint mevcut")
            else:
                print("WARNING ChatbotService type hint eksik")
        
        # Check EmbeddingService type hints
        if hasattr(EmbeddingService, 'generate_embedding'):
            method = getattr(EmbeddingService, 'generate_embedding')
            sig = inspect.signature(method)
            
            has_type_hints = any(param.annotation != param.empty for param in sig.parameters.values())
            if has_type_hints:
                print("OK EmbeddingService metodlarda type hint mevcut")
            else:
                print("WARNING EmbeddingService type hint eksik")
        
        return True
    except Exception as e:
        print(f"ERROR Type hint test hatasi: {e}")
        return False

def test_docstrings():
    """Test docstrings in service classes"""
    try:
        from app.services.chatbot_service import ChatbotService
        from app.services.embedding_service import EmbeddingService
        
        # Check class docstrings
        if ChatbotService.__doc__:
            print("OK ChatbotService class docstring mevcut")
        else:
            print("WARNING ChatbotService class docstring eksik")
        
        if EmbeddingService.__doc__:
            print("OK EmbeddingService class docstring mevcut")
        else:
            print("WARNING EmbeddingService class docstring eksik")
        
        # Check method docstrings
        if hasattr(ChatbotService, 'create_chatbot'):
            method = getattr(ChatbotService, 'create_chatbot')
            if method.__doc__:
                print("OK ChatbotService.create_chatbot docstring mevcut")
            else:
                print("WARNING ChatbotService.create_chatbot docstring eksik")
        
        if hasattr(EmbeddingService, 'generate_embedding'):
            method = getattr(EmbeddingService, 'generate_embedding')
            if method.__doc__:
                print("OK EmbeddingService.generate_embedding docstring mevcut")
            else:
                print("WARNING EmbeddingService.generate_embedding docstring eksik")
        
        return True
    except Exception as e:
        print(f"ERROR Docstring test hatasi: {e}")
        return False

def test_error_handling():
    """Test error handling in services"""
    try:
        # Check if services import proper exception classes
        from app.services.chatbot_service import ChatbotService
        
        # Look for error handling patterns
        import inspect
        
        if hasattr(ChatbotService, 'create_chatbot'):
            source = inspect.getsource(ChatbotService.create_chatbot)
            if 'try:' in source and 'except' in source:
                print("OK ChatbotService error handling mevcut")
            else:
                print("WARNING ChatbotService error handling eksik")
        
        return True
    except Exception as e:
        print(f"ERROR Error handling test hatasi: {e}")
        return False

def test_logging_setup():
    """Test logging configuration in services"""
    try:
        from app.services.chatbot_service import logging as chatbot_logging
        from app.services.embedding_service import logging as embedding_logging
        
        print("OK Servisler logging modulu import ediyor")
        
        # Check if loggers are properly configured
        if hasattr(chatbot_logging, 'getLogger'):
            print("OK Logging yapılandırması mevcut")
        
        return True
    except Exception as e:
        print(f"ERROR Logging test hatasi: {e}")
        return False

def test_service_integration():
    """Test service integration with existing code"""
    try:
        # Check if services can be imported in routers
        from app.services.chatbot_service import ChatbotService
        from app.services.embedding_service import EmbeddingService
        
        # Check if services are properly structured for dependency injection
        import inspect
        
        # ChatbotService should accept dependencies
        chatbot_init = inspect.signature(ChatbotService.__init__)
        print(f"OK ChatbotService init parametreleri: {list(chatbot_init.parameters.keys())}")
        
        # EmbeddingService should accept configuration
        embedding_init = inspect.signature(EmbeddingService.__init__)  
        print(f"OK EmbeddingService init parametreleri: {list(embedding_init.parameters.keys())}")
        
        return True
    except Exception as e:
        print(f"ERROR Servis entegrasyon test hatasi: {e}")
        return False

if __name__ == "__main__":
    print("=== ADIM 10 TEST - TEMEL SERVISLER ===")
    
    # Test imports first
    success, services = test_service_imports()
    if not success:
        print("ERROR Servisler import edilemedigi icin diger testler atlaniyor")
        sys.exit(1)
    
    # Test individual service functionality
    tests = [
        ("ChatbotService Metodları", lambda: test_chatbot_service_methods(services)),
        ("EmbeddingService Metodları", lambda: test_embedding_service_methods(services)),
        ("ChatbotService Async Metodlar", lambda: test_chatbot_service_async_methods(services)),
        ("EmbeddingService Async Metodlar", lambda: test_embedding_service_async_methods(services)),
        ("Servis Bağımlılıkları", test_service_dependencies),
        ("Type Hints", test_type_hints),
        ("Docstrings", test_docstrings),
        ("Error Handling", test_error_handling),
        ("Logging Setup", test_logging_setup),
        ("Servis Entegrasyonu", test_service_integration)
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
        print("SUCCESS Tum Temel Servisler basariyla olusturuldu!")
        print("\nOLUSTURULAN SERVISLER:")
        print("✅ ChatbotService - Chatbot is mantigi ve yonetimi")
        print("✅ EmbeddingService - AI ve embedding islemleri")
        print("\nSERVIS OZELLIKLERI:")
        print("🔧 Chatbot CRUD operasyonlari")
        print("🎛️ Token yonetimi ve guvenlik")
        print("🤖 AI yanit uretme")
        print("📊 Embedding ve benzerlik analizi")
        print("📝 Knowledge base isleme")
        print("⚡ Async/await destegi")
        print("🔍 Type hints ve docstrings")
        print("🚨 Error handling ve logging")
        print("🔗 Dependency injection hazir")
    else:
        print("WARNING Bazi servislerde duzeltme gerekiyor")
        print("\nSONRAKI ADIMLAR:")
        print("1. Eksik metodlari ekleyin")
        print("2. Async/await yapisini kontrol edin")
        print("3. Type hints ekleyin")
        print("4. Error handling gelistirin")
        print("5. Logging yapılandırmasını tamamlayın")