# test_step7.py
import sys
import os
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

def test_model_imports():
    """Test that all models can be imported successfully"""
    try:
        sys.path.append('.')
        from app.models import (
            User, UserCreate,
            Brand, BrandCreate, 
            Chatbot, ChatbotCreate,
            KnowledgeBaseEntry, KnowledgeBaseEntryCreate,
            Conversation, ConversationCreate, Feedback, FeedbackCreate
        )
        print("OK Tum modeller basariyla import edildi")
        return True, {
            'User': User, 'UserCreate': UserCreate,
            'Brand': Brand, 'BrandCreate': BrandCreate,
            'Chatbot': Chatbot, 'ChatbotCreate': ChatbotCreate,
            'KnowledgeBaseEntry': KnowledgeBaseEntry, 
            'KnowledgeBaseEntryCreate': KnowledgeBaseEntryCreate,
            'Conversation': Conversation, 'ConversationCreate': ConversationCreate,
            'Feedback': Feedback, 'FeedbackCreate': FeedbackCreate
        }
    except ImportError as e:
        print(f"ERROR Model import hatasi: {e}")
        return False, {}

def test_user_model(models):
    """Test User model validation"""
    try:
        User = models['User']
        UserCreate = models['UserCreate']
        
        # Valid user test
        user_data = {
            "id": uuid4(),
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "user",
            "created_at": datetime.now()
        }
        user = User(**user_data)
        print("OK User modeli dogru calisiyor")
        
        # UserCreate test
        create_data = {
            "email": "test@example.com",
            "full_name": "Test User"
        }
        user_create = UserCreate(**create_data)
        print("OK UserCreate modeli dogru calisiyor")
        
        return True
    except Exception as e:
        print(f"ERROR User model hatasi: {e}")
        return False

def test_brand_model(models):
    """Test Brand model validation"""
    try:
        Brand = models['Brand']
        BrandCreate = models['BrandCreate']
        
        # Valid brand test
        brand_data = {
            "id": uuid4(),
            "user_id": uuid4(),
            "name": "Test Brand",
            "slug": "test-brand",
            "description": "Test description",
            "theme_color": "#3B82F6",
            "is_active": True,
            "created_at": datetime.now()
        }
        brand = Brand(**brand_data)
        print("OK Brand modeli dogru calisiyor")
        
        # BrandCreate test
        create_data = {
            "name": "Test Brand",
            "description": "Test description"
        }
        brand_create = BrandCreate(**create_data)
        print("OK BrandCreate modeli dogru calisiyor")
        
        return True
    except Exception as e:
        print(f"ERROR Brand model hatasi: {e}")
        return False

def test_chatbot_model(models):
    """Test Chatbot model validation"""
    try:
        Chatbot = models['Chatbot']
        ChatbotCreate = models['ChatbotCreate']
        
        # Valid chatbot test
        chatbot_data = {
            "id": uuid4(),
            "brand_id": uuid4(),
            "name": "Test Bot",
            "primary_color": "#3B82F6",
            "secondary_color": "#EF4444",
            "animation_style": "fade",
            "script_token": str(uuid4()),
            "language": "tr",
            "status": "draft",
            "created_at": datetime.now()
        }
        chatbot = Chatbot(**chatbot_data)
        print("OK Chatbot modeli dogru calisiyor")
        
        # ChatbotCreate test
        create_data = {
            "brand_id": uuid4(),
            "name": "Test Bot"
        }
        chatbot_create = ChatbotCreate(**create_data)
        print("OK ChatbotCreate modeli dogru calisiyor")
        
        return True
    except Exception as e:
        print(f"ERROR Chatbot model hatasi: {e}")
        return False

def test_knowledge_model(models):
    """Test KnowledgeBaseEntry model validation"""
    try:
        KnowledgeBaseEntry = models['KnowledgeBaseEntry']
        KnowledgeBaseEntryCreate = models['KnowledgeBaseEntryCreate']
        
        # Valid knowledge entry test
        knowledge_data = {
            "id": uuid4(),
            "chatbot_id": uuid4(),
            "source_type": "url",
            "source_url": "https://example.com",
            "content": "Test content",
            "token_count": 100,
            "status": "processed",
            "created_at": datetime.now()
        }
        knowledge = KnowledgeBaseEntry(**knowledge_data)
        print("OK KnowledgeBaseEntry modeli dogru calisiyor")
        
        # KnowledgeBaseEntryCreate test
        create_data = {
            "chatbot_id": uuid4(),
            "source_type": "text",
            "content": "Test content"
        }
        knowledge_create = KnowledgeBaseEntryCreate(**create_data)
        print("OK KnowledgeBaseEntryCreate modeli dogru calisiyor")
        
        return True
    except Exception as e:
        print(f"ERROR Knowledge model hatasi: {e}")
        return False

def test_conversation_model(models):
    """Test Conversation model validation"""
    try:
        Conversation = models['Conversation']
        ConversationCreate = models['ConversationCreate']
        Feedback = models['Feedback']
        FeedbackCreate = models['FeedbackCreate']
        
        # Valid conversation test
        conversation_data = {
            "id": uuid4(),
            "chatbot_id": uuid4(),
            "session_id": "test-session",
            "user_input": "Hello",
            "bot_response": "Hi there!",
            "latency_ms": 150,
            "created_at": datetime.now()
        }
        conversation = Conversation(**conversation_data)
        print("OK Conversation modeli dogru calisiyor")
        
        # ConversationCreate test
        create_data = {
            "chatbot_id": uuid4(),
            "session_id": "test-session",
            "user_input": "Hello",
            "bot_response": "Hi there!"
        }
        conversation_create = ConversationCreate(**create_data)
        print("OK ConversationCreate modeli dogru calisiyor")
        
        # Feedback test
        feedback_data = {
            "id": uuid4(),
            "conversation_id": uuid4(),
            "rating": 5,
            "comment": "Great response!",
            "created_at": datetime.now()
        }
        feedback = Feedback(**feedback_data)
        print("OK Feedback modeli dogru calisiyor")
        
        # FeedbackCreate test
        feedback_create_data = {
            "conversation_id": uuid4(),
            "rating": 4,
            "comment": "Good response"
        }
        feedback_create = FeedbackCreate(**feedback_create_data)
        print("OK FeedbackCreate modeli dogru calisiyor")
        
        return True
    except Exception as e:
        print(f"ERROR Conversation model hatasi: {e}")
        return False

def test_model_field_types():
    """Test that models have correct field types"""
    try:
        from app.models import User
        
        # Check if model has proper UUID field
        user_fields = User.model_fields
        if 'id' in user_fields:
            print("OK Model ID field mevcut")
        else:
            print("ERROR Model ID field eksik")
            return False
            
        # Check datetime field
        if 'created_at' in user_fields:
            print("OK Model created_at field mevcut")
        else:
            print("ERROR Model created_at field eksik")
            return False
            
        return True
    except Exception as e:
        print(f"ERROR Field type kontrolu hatasi: {e}")
        return False

if __name__ == "__main__":
    print("=== ADIM 7 TEST - PYDANTIC MODELLERİ ===")
    
    # Test imports first
    success, models = test_model_imports()
    if not success:
        print("ERROR Model import edilemedigi icin diger testler atlaniyor")
        sys.exit(1)
    
    # Test individual models
    tests = [
        ("User Model", lambda: test_user_model(models)),
        ("Brand Model", lambda: test_brand_model(models)),
        ("Chatbot Model", lambda: test_chatbot_model(models)),
        ("Knowledge Model", lambda: test_knowledge_model(models)),
        ("Conversation Model", lambda: test_conversation_model(models)),
        ("Field Types", test_model_field_types)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} Test ---")
        if test_func():
            passed += 1
        
    print(f"\n=== SONUÇ: {passed}/{total} test geçti ===")
    
    if passed == total:
        print("SUCCESS Tum Pydantic modelleri basariyla olusturuldu!")
    else:
        print("WARNING Bazi modellerde duzeltme gerekiyor")