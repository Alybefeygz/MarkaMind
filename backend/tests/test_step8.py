# test_step8.py
import sys
import os
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

def test_schema_imports():
    """Test that all schemas can be imported successfully"""
    try:
        sys.path.append('.')
        from app.schemas import (
            # User schemas
            UserResponse, UserUpdate, UserProfile,
            # Brand schemas  
            BrandResponse, BrandUpdate, BrandList, BrandPublic,
            # Chatbot schemas
            ChatbotResponse, ChatbotUpdate, ChatbotList, ChatbotPublic,
            # Knowledge schemas
            KnowledgeResponse, KnowledgeUpdate, KnowledgeList, KnowledgeStats,
            # Conversation schemas
            ConversationResponse, ConversationList, ConversationStats,
            FeedbackResponse, ChatWidgetMessage,
            # Common schemas
            PaginationParams, PaginationResponse, StatusResponse
        )
        print("OK Tum schemalar basariyla import edildi")
        return True, {
            'UserResponse': UserResponse, 'UserUpdate': UserUpdate, 'UserProfile': UserProfile,
            'BrandResponse': BrandResponse, 'BrandUpdate': BrandUpdate, 
            'BrandList': BrandList, 'BrandPublic': BrandPublic,
            'ChatbotResponse': ChatbotResponse, 'ChatbotUpdate': ChatbotUpdate,
            'ChatbotList': ChatbotList, 'ChatbotPublic': ChatbotPublic,
            'KnowledgeResponse': KnowledgeResponse, 'KnowledgeUpdate': KnowledgeUpdate,
            'KnowledgeList': KnowledgeList, 'KnowledgeStats': KnowledgeStats,
            'ConversationResponse': ConversationResponse, 'ConversationList': ConversationList,
            'ConversationStats': ConversationStats, 'FeedbackResponse': FeedbackResponse,
            'ChatWidgetMessage': ChatWidgetMessage, 'PaginationParams': PaginationParams,
            'PaginationResponse': PaginationResponse, 'StatusResponse': StatusResponse
        }
    except ImportError as e:
        print(f"ERROR Schema import hatasi: {e}")
        return False, {}

def test_user_schemas(schemas):
    """Test User schemas validation"""
    try:
        UserResponse = schemas['UserResponse']
        UserUpdate = schemas['UserUpdate']
        UserProfile = schemas['UserProfile']
        
        # Valid UserResponse test
        user_response_data = {
            "id": uuid4(),
            "email": "test@example.com", 
            "full_name": "Test User",
            "role": "user",
            "created_at": datetime.now()
        }
        user_response = UserResponse(**user_response_data)
        print("OK UserResponse schema dogru calisiyor")
        
        # UserUpdate test
        user_update_data = {
            "full_name": "Updated Name"
        }
        user_update = UserUpdate(**user_update_data)
        print("OK UserUpdate schema dogru calisiyor")
        
        # UserProfile test  
        user_profile_data = {
            "id": uuid4(),
            "full_name": "Test User",
            "role": "user"
        }
        user_profile = UserProfile(**user_profile_data)
        print("OK UserProfile schema dogru calisiyor")
        
        return True
    except Exception as e:
        print(f"ERROR User schema hatasi: {e}")
        return False

def test_brand_schemas(schemas):
    """Test Brand schemas validation"""
    try:
        BrandResponse = schemas['BrandResponse']
        BrandUpdate = schemas['BrandUpdate']
        BrandList = schemas['BrandList']
        BrandPublic = schemas['BrandPublic']
        
        # BrandResponse test
        brand_response_data = {
            "id": uuid4(),
            "user_id": uuid4(),
            "name": "Test Brand",
            "slug": "test-brand",
            "description": "Test description",
            "theme_color": "#3B82F6",
            "is_active": True,
            "created_at": datetime.now()
        }
        brand_response = BrandResponse(**brand_response_data)
        print("OK BrandResponse schema dogru calisiyor")
        
        # BrandUpdate test
        brand_update_data = {
            "name": "Updated Brand",
            "theme_color": "#EF4444"
        }
        brand_update = BrandUpdate(**brand_update_data)
        print("OK BrandUpdate schema dogru calisiyor")
        
        # BrandList test
        brand_list_data = {
            "id": uuid4(),
            "name": "Test Brand",
            "slug": "test-brand",
            "theme_color": "#3B82F6",
            "is_active": True
        }
        brand_list = BrandList(**brand_list_data)
        print("OK BrandList schema dogru calisiyor")
        
        # BrandPublic test
        brand_public_data = {
            "name": "Test Brand",
            "theme_color": "#3B82F6"
        }
        brand_public = BrandPublic(**brand_public_data)
        print("OK BrandPublic schema dogru calisiyor")
        
        return True
    except Exception as e:
        print(f"ERROR Brand schema hatasi: {e}")
        return False

def test_chatbot_schemas(schemas):
    """Test Chatbot schemas validation"""
    try:
        ChatbotResponse = schemas['ChatbotResponse']
        ChatbotUpdate = schemas['ChatbotUpdate']
        ChatbotList = schemas['ChatbotList']
        ChatbotPublic = schemas['ChatbotPublic']
        
        # ChatbotResponse test
        chatbot_response_data = {
            "id": uuid4(),
            "brand_id": uuid4(),
            "name": "Test Bot",
            "primary_color": "#3B82F6",
            "secondary_color": "#EF4444",
            "animation_style": "fade",
            "script_token": str(uuid4()),
            "language": "tr",
            "status": "active",
            "created_at": datetime.now()
        }
        chatbot_response = ChatbotResponse(**chatbot_response_data)
        print("OK ChatbotResponse schema dogru calisiyor")
        
        # ChatbotUpdate test
        chatbot_update_data = {
            "name": "Updated Bot",
            "primary_color": "#10B981"
        }
        chatbot_update = ChatbotUpdate(**chatbot_update_data)
        print("OK ChatbotUpdate schema dogru calisiyor")
        
        # ChatbotList test
        chatbot_list_data = {
            "id": uuid4(),
            "name": "Test Bot",
            "primary_color": "#3B82F6",
            "status": "active"
        }
        chatbot_list = ChatbotList(**chatbot_list_data)
        print("OK ChatbotList schema dogru calisiyor")
        
        # ChatbotPublic test
        chatbot_public_data = {
            "name": "Test Bot",
            "primary_color": "#3B82F6",
            "secondary_color": "#EF4444",
            "script_token": str(uuid4()),
            "language": "tr"
        }
        chatbot_public = ChatbotPublic(**chatbot_public_data)
        print("OK ChatbotPublic schema dogru calisiyor")
        
        return True
    except Exception as e:
        print(f"ERROR Chatbot schema hatasi: {e}")
        return False

def test_knowledge_schemas(schemas):
    """Test Knowledge schemas validation"""
    try:
        KnowledgeResponse = schemas['KnowledgeResponse']
        KnowledgeUpdate = schemas['KnowledgeUpdate']
        KnowledgeList = schemas['KnowledgeList']
        KnowledgeStats = schemas['KnowledgeStats']
        
        # KnowledgeResponse test
        knowledge_response_data = {
            "id": uuid4(),
            "chatbot_id": uuid4(),
            "source_type": "url",
            "source_url": "https://example.com",
            "content": "Test content",
            "token_count": 100,
            "status": "processed",
            "created_at": datetime.now()
        }
        knowledge_response = KnowledgeResponse(**knowledge_response_data)
        print("OK KnowledgeResponse schema dogru calisiyor")
        
        # KnowledgeUpdate test
        knowledge_update_data = {
            "content": "Updated content",
            "status": "processed"
        }
        knowledge_update = KnowledgeUpdate(**knowledge_update_data)
        print("OK KnowledgeUpdate schema dogru calisiyor")
        
        # KnowledgeList test
        knowledge_list_data = {
            "id": uuid4(),
            "source_type": "url",
            "source_url": "https://example.com",
            "status": "processed",
            "token_count": 100,
            "created_at": datetime.now()
        }
        knowledge_list = KnowledgeList(**knowledge_list_data)
        print("OK KnowledgeList schema dogru calisiyor")
        
        # KnowledgeStats test
        knowledge_stats_data = {
            "total_entries": 10,
            "total_tokens": 5000,
            "status_counts": {"processed": 8, "pending": 2}
        }
        knowledge_stats = KnowledgeStats(**knowledge_stats_data)
        print("OK KnowledgeStats schema dogru calisiyor")
        
        return True
    except Exception as e:
        print(f"ERROR Knowledge schema hatasi: {e}")
        return False

def test_conversation_schemas(schemas):
    """Test Conversation schemas validation"""
    try:
        ConversationResponse = schemas['ConversationResponse']
        ConversationList = schemas['ConversationList']
        ConversationStats = schemas['ConversationStats']
        FeedbackResponse = schemas['FeedbackResponse']
        ChatWidgetMessage = schemas['ChatWidgetMessage']
        
        # ConversationResponse test
        conversation_response_data = {
            "id": uuid4(),
            "chatbot_id": uuid4(),
            "session_id": "test-session",
            "user_input": "Hello",
            "bot_response": "Hi there!",
            "latency_ms": 150,
            "created_at": datetime.now()
        }
        conversation_response = ConversationResponse(**conversation_response_data)
        print("OK ConversationResponse schema dogru calisiyor")
        
        # ConversationList test
        conversation_list_data = {
            "id": uuid4(),
            "user_input": "Hello",
            "bot_response": "Hi there!",
            "latency_ms": 150,
            "created_at": datetime.now()
        }
        conversation_list = ConversationList(**conversation_list_data)
        print("OK ConversationList schema dogru calisiyor")
        
        # ConversationStats test
        conversation_stats_data = {
            "total_conversations": 100,
            "avg_latency": 200.5,
            "rating_avg": 4.5
        }
        conversation_stats = ConversationStats(**conversation_stats_data)
        print("OK ConversationStats schema dogru calisiyor")
        
        # FeedbackResponse test
        feedback_response_data = {
            "id": uuid4(),
            "conversation_id": uuid4(),
            "rating": 5,
            "comment": "Great!",
            "created_at": datetime.now()
        }
        feedback_response = FeedbackResponse(**feedback_response_data)
        print("OK FeedbackResponse schema dogru calisiyor")
        
        # ChatWidgetMessage test
        widget_message_data = {
            "message": "Hello from widget",
            "timestamp": datetime.now(),
            "is_user": True
        }
        widget_message = ChatWidgetMessage(**widget_message_data)
        print("OK ChatWidgetMessage schema dogru calisiyor")
        
        return True
    except Exception as e:
        print(f"ERROR Conversation schema hatasi: {e}")
        return False

def test_common_schemas(schemas):
    """Test Common schemas validation"""
    try:
        PaginationParams = schemas['PaginationParams']
        PaginationResponse = schemas['PaginationResponse']
        StatusResponse = schemas['StatusResponse']
        
        # PaginationParams test
        pagination_params_data = {
            "page": 1,
            "size": 10,
            "sort": "created_at"
        }
        pagination_params = PaginationParams(**pagination_params_data)
        print("OK PaginationParams schema dogru calisiyor")
        
        # PaginationResponse test - Generic type with dict data
        pagination_response_data = {
            "items": [{"id": 1, "name": "test"}],
            "total": 1,
            "page": 1,
            "size": 10,
            "pages": 1
        }
        pagination_response = PaginationResponse(**pagination_response_data)
        print("OK PaginationResponse schema dogru calisiyor")
        
        # StatusResponse test
        status_response_data = {
            "success": True,
            "message": "Operation successful"
        }
        status_response = StatusResponse(**status_response_data)
        print("OK StatusResponse schema dogru calisiyor")
        
        return True
    except Exception as e:
        print(f"ERROR Common schema hatasi: {e}")
        return False

if __name__ == "__main__":
    print("=== ADIM 8 TEST - REQUEST/RESPONSE SEMALARI ===")
    
    # Test imports first
    success, schemas = test_schema_imports()
    if not success:
        print("ERROR Schema import edilemedigi icin diger testler atlaniyor")
        sys.exit(1)
    
    # Test individual schema groups
    tests = [
        ("User Schemas", lambda: test_user_schemas(schemas)),
        ("Brand Schemas", lambda: test_brand_schemas(schemas)),
        ("Chatbot Schemas", lambda: test_chatbot_schemas(schemas)),
        ("Knowledge Schemas", lambda: test_knowledge_schemas(schemas)),
        ("Conversation Schemas", lambda: test_conversation_schemas(schemas)),
        ("Common Schemas", lambda: test_common_schemas(schemas))
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} Test ---")
        if test_func():
            passed += 1
        
    print(f"\n=== SONUC: {passed}/{total} test gecti ===")
    
    if passed == total:
        print("SUCCESS Tum Request/Response semalari basariyla olusturuldu!")
    else:
        print("WARNING Bazi semalarda duzeltme gerekiyor")