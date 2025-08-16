# MarkaMind FastAPI Backend Kurulum Rehberi

Bu rehber, MarkaMind projesi için FastAPI backend'ini adım adım kurmak için hazırlanmıştır. Her adımı sırasıyla takip ederek temel seviyede çalışan bir backend elde edeceksiniz.

## 📋 TODO LİSTESİ

### ✅ 1. Geliştirme Ortamı Hazırlığı

**Etkilenen Dosyalar:**
- backend/ (klasör)
- venv/ (klasör - oluşturulacak)

**Yapılacaklar:**
- [X] Python 3.9+ yüklü olduğunu kontrol et
- [X] backend klasörüne git
- [X] Virtual environment oluştur (`python -m venv venv`)
- [X] Virtual environment'ı aktive et (`venv\Scripts\activate` - Windows)

**Detaylı Prompt:**
```
1. Öncelikle Python versiyonunu kontrol et: `python --version`
2. Backend klasörüne git: `cd backend`
3. Virtual environment oluştur: `python -m venv venv`
4. Virtual environment'ı aktive et:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
5. Aktivasyon sonrası terminalde (venv) ifadesini gör
```

**Test Scripti:**
```python
# test_step1.py
import subprocess
import sys
import os

def test_python_version():
    try:
        result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"✅ Python versiyonu: {version}")
        
        # Python 3.9+ kontrolü
        version_info = sys.version_info
        if version_info >= (3, 9):
            print("✅ Python versiyonu uygun (3.9+)")
            return True
        else:
            print("❌ Python 3.9+ gerekli")
            return False
    except Exception as e:
        print(f"❌ Python kontrol hatası: {e}")
        return False

def test_venv_exists():
    if os.path.exists('venv'):
        print("✅ Virtual environment mevcut")
        return True
    else:
        print("❌ Virtual environment bulunamadı")
        return False

def test_venv_activated():
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment aktif")
        return True
    else:
        print("❌ Virtual environment aktif değil")
        return False

if __name__ == "__main__":
    print("=== ADIM 1 TEST ===")
    test_python_version()
    test_venv_exists()
    test_venv_activated()
```

**Hata Çözme Promtu:**
```
Olası hatalar ve çözümleri:

1. "python komutu bulunamadı":
   - Windows: Python Store'dan Python yükle veya python.org'dan indir
   - PATH değişkenine Python'u ekle

2. "Virtual environment oluşturulamadı":
   - `python -m pip install --upgrade pip`
   - `python -m pip install virtualenv`

3. "Permission denied" hatası:
   - Windows: PowerShell'i admin olarak çalıştır
   - Linux/Mac: sudo kullanma, user permissions kontrol et

4. Virtual environment aktive olmuyorsa:
   - Windows: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
   - Komut dosyasını tam path ile çalıştır
```

### ✅ 2. Bağımlılık Yönetimi

**Etkilenen Dosyalar:**
- backend/requirements.txt (oluşturulacak)
- venv/lib/site-packages/ (paketler yüklenecek)

**Yapılacaklar:**
- [X] requirements.txt dosyası oluştur
- [X] Temel FastAPI bağımlılıklarını yükle (`pip install -r requirements.txt`)
- [X] requirements.txt'yi güncel tut (`pip freeze > requirements.txt`)

**Detaylı Prompt:**
```
1. requirements.txt dosyasını oluştur ve aşağıdaki içeriği ekle:
   - fastapi==0.104.1
   - uvicorn[standard]==0.24.0
   - pydantic==2.5.0
   - python-dotenv==1.0.0
   - python-multipart==0.0.6
   - supabase==2.2.0
   - python-jose[cryptography]==3.3.0
   - passlib[bcrypt]==1.7.4
   - python-dateutil==2.8.2
   - requests==2.31.0
   - openai==1.3.0 (OpenRouter için)

2. Virtual environment'ın aktif olduğundan emin ol
3. Paketleri yükle: `pip install -r requirements.txt`
4. Kurulum kontrolü: `pip list`
5. requirements.txt güncel tut: `pip freeze > requirements.txt`
```

**Test Scripti:**
```python
# test_step2.py
import subprocess
import sys
import os

def test_requirements_file():
    if os.path.exists('requirements.txt'):
        print("✅ requirements.txt dosyası mevcut")
        with open('requirements.txt', 'r') as f:
            content = f.read()
            required_packages = ['fastapi', 'uvicorn', 'supabase', 'openai']
            for package in required_packages:
                if package in content.lower():
                    print(f"✅ {package} requirements.txt'de bulundu")
                else:
                    print(f"❌ {package} requirements.txt'de bulunamadı")
        return True
    else:
        print("❌ requirements.txt dosyası bulunamadı")
        return False

def test_packages_installed():
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        installed_packages = result.stdout.lower()
        
        critical_packages = ['fastapi', 'uvicorn', 'supabase', 'openai']
        all_installed = True
        
        for package in critical_packages:
            if package in installed_packages:
                print(f"✅ {package} yüklü")
            else:
                print(f"❌ {package} yüklü değil")
                all_installed = False
                
        return all_installed
    except Exception as e:
        print(f"❌ Paket kontrol hatası: {e}")
        return False

def test_venv_activated():
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment aktif")
        return True
    else:
        print("❌ Virtual environment aktif değil - Paketler sistem geneline yüklenebilir!")
        return False

if __name__ == "__main__":
    print("=== ADIM 2 TEST ===")
    test_venv_activated()
    test_requirements_file() 
    test_packages_installed()
```

**Hata Çözme Promtu:**
```
Olası hatalar ve çözümleri:

1. "pip install başarısız":
   - `python -m pip install --upgrade pip`
   - `pip install --upgrade setuptools wheel`
   - Tek tek paket yükle ve hangi pakette hata aldığını bul

2. "Permission denied" pip install:
   - Virtual environment aktif mi kontrol et
   - Windows: admin terminal kullan
   - `pip install --user` ile kullanıcı bazlı yükle

3. "Package bulunamadı" hatası:
   - İnternet bağlantısı kontrol et
   - `pip install --index-url https://pypi.org/simple/`
   - Proxy ayarları kontrol et

4. "Conflicting dependencies":
   - `pip install --force-reinstall`
   - requirements.txt'deki versiyonları güncel tut
   - `pip-tools` kullanarak dependency çözümle

5. OpenAI paketi sorunları:
   - `pip install openai==1.3.0` ile spesifik versiyon yükle
   - OpenRouter, OpenAI client'ını kullanır
```

### ✅ 3. Proje Klasör Yapısı

**Etkilenen Dosyalar:**
- app/ (tüm klasör yapısı oluşturulacak)
- app/__init__.py
- app/models/__init__.py  
- app/schemas/__init__.py
- app/routers/__init__.py
- app/services/__init__.py
- app/utils/__init__.py
- migrations/ (klasör)
- tests/ (klasör)

**Yapılacaklar:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI uygulaması
│   ├── config.py              # Konfigürasyon ayarları
│   ├── database.py            # Supabase bağlantısı
│   ├── dependencies.py        # JWT auth vb. dependencies
│   │
│   ├── models/                # Pydantic modelleri
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── brand.py
│   │   ├── chatbot.py
│   │   ├── knowledge.py
│   │   └── conversation.py
│   │
│   ├── schemas/               # Request/Response şemaları
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── brand.py
│   │   ├── chatbot.py
│   │   ├── knowledge.py
│   │   └── conversation.py
│   │
│   ├── routers/               # API endpoint'leri
│   │   ├── __init__.py
│   │   ├── auth.py            # /me endpoints
│   │   ├── brands.py          # /brands endpoints
│   │   ├── chatbots.py        # /chatbots endpoints
│   │   ├── knowledge.py       # /knowledge endpoints
│   │   ├── conversations.py   # /conversations endpoints
│   │   ├── uploads.py         # /uploads endpoints
│   │   ├── widget.py          # /widget endpoints
│   │   └── feedback.py        # /feedback endpoints
│   │
│   ├── services/              # İş mantığı servisleri
│   │   ├── __init__.py
│   │   ├── supabase_service.py
│   │   ├── auth_service.py
│   │   ├── chatbot_service.py
│   │   ├── openrouter_service.py  # OpenRouter AI servisi
│   │   └── embedding_service.py
│   │
│   └── utils/                 # Yardımcı fonksiyonlar
│       ├── __init__.py
│       ├── security.py        # JWT token işlemleri
│       └── helpers.py
│
├── migrations/                # Veritabanı migration'ları
├── tests/                     # Test dosyaları
├── .env                       # Ortam değişkenleri
├── .env.example              # Örnek ortam değişkenleri
├── requirements.txt          # Python bağımlılıkları
├── markamind.md             # Proje dokümantasyonu (mevcut)
└── setup-fastapi.md         # Bu dosya
```

**Detaylı Prompt:**
```
1. Ana klasörleri oluştur:
   mkdir -p app/models app/schemas app/routers app/services app/utils
   mkdir -p migrations tests

2. Tüm __init__.py dosyalarını oluştur:
   touch app/__init__.py
   touch app/models/__init__.py
   touch app/schemas/__init__.py  
   touch app/routers/__init__.py
   touch app/services/__init__.py
   touch app/utils/__init__.py

3. Ana dosyaları oluştur (boş):
   touch app/main.py app/config.py app/database.py app/dependencies.py

4. Model dosyalarını oluştur:
   touch app/models/user.py app/models/brand.py app/models/chatbot.py
   touch app/models/knowledge.py app/models/conversation.py

5. Schema dosyalarını oluştur:
   touch app/schemas/user.py app/schemas/brand.py app/schemas/chatbot.py
   touch app/schemas/knowledge.py app/schemas/conversation.py

6. Router dosyalarını oluştur:
   touch app/routers/auth.py app/routers/brands.py app/routers/chatbots.py
   touch app/routers/knowledge.py app/routers/conversations.py
   touch app/routers/uploads.py app/routers/widget.py app/routers/feedback.py

7. Service dosyalarını oluştur:
   touch app/services/supabase_service.py app/services/auth_service.py
   touch app/services/chatbot_service.py app/services/openrouter_service.py
   touch app/services/embedding_service.py

8. Utility dosyalarını oluştur:
   touch app/utils/security.py app/utils/helpers.py
```

**Test Scripti:**
```python
# test_step3.py
import os

def test_folder_structure():
    expected_folders = [
        'app',
        'app/models',
        'app/schemas', 
        'app/routers',
        'app/services',
        'app/utils',
        'migrations',
        'tests'
    ]
    
    all_exists = True
    for folder in expected_folders:
        if os.path.exists(folder):
            print(f"✅ {folder} klasörü mevcut")
        else:
            print(f"❌ {folder} klasörü bulunamadı")
            all_exists = False
    
    return all_exists

def test_init_files():
    expected_init_files = [
        'app/__init__.py',
        'app/models/__init__.py',
        'app/schemas/__init__.py',
        'app/routers/__init__.py', 
        'app/services/__init__.py',
        'app/utils/__init__.py'
    ]
    
    all_exists = True
    for init_file in expected_init_files:
        if os.path.exists(init_file):
            print(f"✅ {init_file} mevcut")
        else:
            print(f"❌ {init_file} bulunamadı")
            all_exists = False
    
    return all_exists

def test_core_files():
    core_files = [
        'app/main.py',
        'app/config.py', 
        'app/database.py',
        'app/dependencies.py'
    ]
    
    all_exists = True
    for core_file in core_files:
        if os.path.exists(core_file):
            print(f"✅ {core_file} mevcut")
        else:
            print(f"❌ {core_file} bulunamadı") 
            all_exists = False
    
    return all_exists

def test_service_files():
    service_files = [
        'app/services/openrouter_service.py',
        'app/services/supabase_service.py',
        'app/services/auth_service.py'
    ]
    
    all_exists = True
    for service_file in service_files:
        if os.path.exists(service_file):
            print(f"✅ {service_file} mevcut")
        else:
            print(f"❌ {service_file} bulunamadı")
            all_exists = False
            
    return all_exists

if __name__ == "__main__":
    print("=== ADIM 3 TEST ===")
    test_folder_structure()
    test_init_files()
    test_core_files()
    test_service_files()
```

**Hata Çözme Promtu:**
```
Olası hatalar ve çözümleri:

1. "mkdir komutu bulunamadı" (Windows):
   - PowerShell kullan: `New-Item -ItemType Directory -Path "app\models"`
   - Veya Windows Explorer'dan manuel oluştur

2. "touch komutu bulunamadı" (Windows):
   - PowerShell: `New-Item -ItemType File -Path "app\main.py"`
   - Veya text editör ile boş dosyalar oluştur

3. "Permission denied" klasör oluşturma:
   - Klasörün write permission'ı kontrol et
   - Admin yetkisi ile çalıştır

4. __init__.py dosyaları eksik:
   - Python paketleri olabilmesi için gerekli
   - Boş bırakılabilir ama mutlaka bulunmalı

5. Klasör yapısı karmaşık geliyorsa:
   - Önce temel klasörleri oluştur (app, app/routers, app/services)
   - Sonra detayları ekle
   - Her klasör için test scriptini çalıştır
```

### ✅ 4. Temel Dosyaları Oluştur
- [X] `.env.example` dosyası oluştur
- [X] `.env` dosyası oluştur ve Supabase bilgilerini ekle
- [X] `app/__init__.py` dosyaları oluştur
- [X] `app/config.py` - Konfigürasyon ayarları
- [X] `app/main.py` - Ana FastAPI uygulaması

### ✅ 5. Supabase Entegrasyonu
- [X] `app/database.py` - Supabase client bağlantısı
- [X] `app/services/supabase_service.py` - Supabase işlemleri
- [X] Supabase tabloları oluştur (SQL script'leri hazırla)
- [X] Bağlantı testi yap

### ✅ 6. Authentication Sistemi
- [X] `app/dependencies.py` - JWT doğrulama
- [X] `app/utils/security.py` - Token işlemleri
- [X] `app/services/auth_service.py` - Auth servisi
- [X] `app/routers/auth.py` - Auth endpoint'leri

### ✅ 7. Pydantic Modelleri

**Etkilenen Dosyalar:**
- `app/models/__init__.py` (içe aktarma işlemleri)
- `app/models/user.py` (User modeli)
- `app/models/brand.py` (Brand modeli)
- `app/models/chatbot.py` (Chatbot modeli)
- `app/models/knowledge.py` (KnowledgeBase modeli)
- `app/models/conversation.py` (Conversation modeli)

**Yapılacaklar:**
- [X] User model'i oluştur (profil bilgileri, rol yönetimi)
- [X] Brand model'i oluştur (marka bilgileri, tema ayarları)
- [X] Chatbot model'i oluştur (chatbot konfigürasyonu, renk ayarları)
- [X] Knowledge model'i oluştur (bilgi kaynakları, embedding)
- [X] Conversation model'i oluştur (konuşma geçmişi, feedback)

**Detaylı Prompt:**
```python
# Bu adımda Supabase tablolarınıza uygun Pydantic modellerini oluşturacaksınız.
# Her model, veritabanı tablolarıyla tam uyumlu olmalı ve Supabase'den gelen
# UUID, datetime gibi veri tiplerini doğru şekilde işlemelidir.

1. app/models/user.py - Kullanıcı modeli:
   - BaseModel'den inherit et
   - UUID id field'ı
   - email (str), full_name (Optional[str])
   - role (str, default="user")
   - created_at (datetime)
   - Config class ile from_attributes = True

2. app/models/brand.py - Marka modeli:
   - Brand ve BrandCreate sınıfları
   - UUID id, user_id field'ları
   - name, slug, description, logo_url
   - theme_color (default="#3B82F6")
   - is_active (bool)
   - created_at

3. app/models/chatbot.py - Chatbot modeli:
   - Chatbot ve ChatbotCreate sınıfları
   - UUID id, brand_id
   - name, avatar_url
   - primary_color, secondary_color, animation_style
   - script_token (UUID), language, status
   - created_at

4. app/models/knowledge.py - Bilgi kaynağı modeli:
   - KnowledgeBaseEntry ve KnowledgeBaseEntryCreate
   - UUID id, chatbot_id
   - source_type, source_url, content
   - embedding_id, token_count, status
   - created_at

5. app/models/conversation.py - Konuşma modeli:
   - Conversation ve ConversationCreate
   - UUID id, chatbot_id, source_entry_id
   - session_id, user_input, bot_response
   - latency_ms, created_at
   - Feedback sınıfı da dahil et

6. app/models/__init__.py - Tüm modelleri import et:
   from .user import User, UserCreate
   from .brand import Brand, BrandCreate
   from .chatbot import Chatbot, ChatbotCreate
   from .knowledge import KnowledgeBaseEntry, KnowledgeBaseEntryCreate
   from .conversation import Conversation, ConversationCreate, Feedback
```

**Test Scripti:**
```python
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
            Conversation, ConversationCreate, Feedback
        )
        print("✅ Tüm modeller başarıyla import edildi")
        return True, {
            'User': User, 'UserCreate': UserCreate,
            'Brand': Brand, 'BrandCreate': BrandCreate,
            'Chatbot': Chatbot, 'ChatbotCreate': ChatbotCreate,
            'KnowledgeBaseEntry': KnowledgeBaseEntry, 
            'KnowledgeBaseEntryCreate': KnowledgeBaseEntryCreate,
            'Conversation': Conversation, 'ConversationCreate': ConversationCreate,
            'Feedback': Feedback
        }
    except ImportError as e:
        print(f"❌ Model import hatası: {e}")
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
        print("✅ User modeli doğru çalışıyor")
        
        # UserCreate test
        create_data = {
            "email": "test@example.com",
            "full_name": "Test User"
        }
        user_create = UserCreate(**create_data)
        print("✅ UserCreate modeli doğru çalışıyor")
        
        return True
    except Exception as e:
        print(f"❌ User model hatası: {e}")
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
        print("✅ Brand modeli doğru çalışıyor")
        
        # BrandCreate test
        create_data = {
            "name": "Test Brand",
            "description": "Test description"
        }
        brand_create = BrandCreate(**create_data)
        print("✅ BrandCreate modeli doğru çalışıyor")
        
        return True
    except Exception as e:
        print(f"❌ Brand model hatası: {e}")
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
        print("✅ Chatbot modeli doğru çalışıyor")
        
        # ChatbotCreate test
        create_data = {
            "brand_id": uuid4(),
            "name": "Test Bot"
        }
        chatbot_create = ChatbotCreate(**create_data)
        print("✅ ChatbotCreate modeli doğru çalışıyor")
        
        return True
    except Exception as e:
        print(f"❌ Chatbot model hatası: {e}")
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
        print("✅ KnowledgeBaseEntry modeli doğru çalışıyor")
        
        # KnowledgeBaseEntryCreate test
        create_data = {
            "chatbot_id": uuid4(),
            "source_type": "text",
            "content": "Test content"
        }
        knowledge_create = KnowledgeBaseEntryCreate(**create_data)
        print("✅ KnowledgeBaseEntryCreate modeli doğru çalışıyor")
        
        return True
    except Exception as e:
        print(f"❌ Knowledge model hatası: {e}")
        return False

def test_conversation_model(models):
    """Test Conversation model validation"""
    try:
        Conversation = models['Conversation']
        ConversationCreate = models['ConversationCreate']
        Feedback = models['Feedback']
        
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
        print("✅ Conversation modeli doğru çalışıyor")
        
        # ConversationCreate test
        create_data = {
            "chatbot_id": uuid4(),
            "session_id": "test-session",
            "user_input": "Hello",
            "bot_response": "Hi there!"
        }
        conversation_create = ConversationCreate(**create_data)
        print("✅ ConversationCreate modeli doğru çalışıyor")
        
        # Feedback test
        feedback_data = {
            "id": uuid4(),
            "conversation_id": uuid4(),
            "rating": 5,
            "comment": "Great response!",
            "created_at": datetime.now()
        }
        feedback = Feedback(**feedback_data)
        print("✅ Feedback modeli doğru çalışıyor")
        
        return True
    except Exception as e:
        print(f"❌ Conversation model hatası: {e}")
        return False

def test_model_field_types():
    """Test that models have correct field types"""
    try:
        from app.models import User
        
        # Check if model has proper UUID field
        user_fields = User.model_fields
        if 'id' in user_fields:
            print("✅ Model ID field'ı mevcut")
        else:
            print("❌ Model ID field'ı eksik")
            return False
            
        # Check datetime field
        if 'created_at' in user_fields:
            print("✅ Model created_at field'ı mevcut")
        else:
            print("❌ Model created_at field'ı eksik")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Field type kontrolü hatası: {e}")
        return False

if __name__ == "__main__":
    print("=== ADIM 7 TEST - PYDANTIC MODELLERİ ===")
    
    # Test imports first
    success, models = test_model_imports()
    if not success:
        print("❌ Model import edilemediği için diğer testler atlanıyor")
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
        print("🎉 Tüm Pydantic modelleri başarıyla oluşturuldu!")
    else:
        print("⚠️  Bazı modellerde düzeltme gerekiyor")
```

**Hata Çözme Promtu:**
```python
# Olası hatalar ve çözümleri:

1. "pydantic import hatası":
   - `pip install pydantic==2.5.0` ile doğru versiyon yükle
   - Virtual environment aktif mi kontrol et
   - `from pydantic import BaseModel` import'u doğru mu?

2. "UUID field validation hatası":
   - `from uuid import UUID` import'unu ekle
   - UUID field'larını Optional[UUID] = None olarak tanımla (Create modellerde)
   - Supabase'den gelen UUID'ler string olabilir, validation ekle

3. "datetime field hatası":
   - `from datetime import datetime` import'unu ekle
   - Optional[datetime] = None kullan (Create modellerde)
   - timezone aware datetime kullan: `datetime.now(timezone.utc)`

4. "Model validation hatası":
   - Field type'ları Supabase tablolarıyla uyumlu mu kontrol et
   - Optional field'ları doğru tanımladın mı?
   - Default değerleri set et: `status: str = "draft"`

5. "Config class hatası":
   - Pydantic v2 syntax: `model_config = ConfigDict(from_attributes=True)`
   - Eski syntax: `class Config: orm_mode = True` (deprecated)

6. "Import circular dependency":
   - TYPE_CHECKING kullan: `from typing import TYPE_CHECKING`
   - Forward reference'lar için string annotation: `brand: "Brand"`

7. "Field naming conflict":
   - Python keyword'ları field name olarak kullanma
   - alias kullan: `type_: str = Field(alias="type")`

8. Model inheritance sorunları:
   - Base model oluştur: `class BaseModel(PydanticBaseModel)`
   - Common field'ları base'e taşı (id, created_at)

9. Validation rules eksik:
   - Email field için EmailStr kullan: `email: EmailStr`
   - URL field'ları için HttpUrl kullan
   - Regex validation: `slug: str = Field(regex=r'^[a-z0-9-]+$')`

10. JSON serialization sorunları:
    - UUID'leri string'e çevir: `model_dump(mode='json')`
    - datetime format'ı: ISO format kullan
```

### ✅ 8. Request/Response Şemaları

**Etkilenen Dosyalar:**
- `app/schemas/__init__.py` (içe aktarma işlemleri)
- `app/schemas/user.py` (User şemaları - Response, Update)
- `app/schemas/brand.py` (Brand şemaları - Create, Update, Response, List)
- `app/schemas/chatbot.py` (Chatbot şemaları - Create, Update, Response, List)
- `app/schemas/knowledge.py` (Knowledge şemaları - Create, Update, Response, List)
- `app/schemas/conversation.py` (Conversation şemaları - Create, Response, List)

**Yapılacaklar:**
- [X] User schema'ları oluştur (UserResponse, UserUpdate)
- [X] Brand schema'ları oluştur (BrandResponse, BrandUpdate, BrandList)
- [X] Chatbot schema'ları oluştur (ChatbotResponse, ChatbotUpdate, ChatbotList)
- [X] Knowledge schema'ları oluştur (KnowledgeResponse, KnowledgeUpdate, KnowledgeList)
- [X] Conversation schema'ları oluştur (ConversationResponse, ConversationList, FeedbackResponse)

**Detaylı Prompt:**
```python
# Bu adımda API endpoint'leri için Request/Response şemalarını oluşturacaksınız.
# Schemas, models'den farklı olarak API'nin dış dünyaya gösterdiği veri yapılarıdır.
# Bazı field'lar gizlenmeli (password, private keys) veya ekstra field'lar eklenmelidir.

1. app/schemas/user.py - Kullanıcı şemaları:
   - UserResponse: API'nin döndüğü user bilgileri (id, email, full_name, role, created_at)
   - UserUpdate: Kullanıcı güncelleme için (full_name, role - opsiyonel)
   - UserProfile: Profil bilgileri (sadece public bilgiler)

2. app/schemas/brand.py - Marka şemaları:
   - BrandResponse: Tam brand bilgileri (id, user_id, name, slug, description, logo_url, theme_color, is_active, created_at)
   - BrandUpdate: Brand güncelleme (name, description, logo_url, theme_color, is_active - tümü opsiyonel)
   - BrandList: Liste için kısaltılmış bilgiler (id, name, slug, logo_url, theme_color, is_active)
   - BrandPublic: Public widget için (sadece name, logo_url, theme_color)

3. app/schemas/chatbot.py - Chatbot şemaları:
   - ChatbotResponse: Tam chatbot bilgileri (tüm field'lar + brand bilgisi)
   - ChatbotUpdate: Chatbot güncelleme (name, avatar_url, colors, animation_style, language, status)
   - ChatbotList: Liste için kısaltılmış (id, name, avatar_url, primary_color, status)
   - ChatbotPublic: Widget için public bilgiler (name, avatar_url, colors, script_token)

4. app/schemas/knowledge.py - Bilgi kaynağı şemaları:
   - KnowledgeResponse: Tam knowledge entry bilgileri
   - KnowledgeUpdate: Güncelleme (content, status)
   - KnowledgeList: Liste için (id, source_type, source_url başlangıcı, status, created_at)
   - KnowledgeStats: İstatistikler (total_entries, total_tokens, status_counts)

5. app/schemas/conversation.py - Konuşma şemaları:
   - ConversationResponse: Tam konuşma bilgileri
   - ConversationList: Liste için kısaltılmış (id, user_input başlangıcı, created_at)
   - ConversationStats: İstatistikler (total_conversations, avg_latency, rating_avg)
   - FeedbackResponse: Feedback bilgileri
   - ChatWidgetMessage: Widget için mesaj formatı

6. app/schemas/common.py - Ortak şemalar:
   - PaginationParams: Sayfalama parametreleri (page, size, sort)
   - PaginationResponse: Sayfalama cevabı (items, total, page, size, pages)
   - StatusResponse: Başarı/hata mesajları
   - FileUploadResponse: Dosya yükleme cevabı

7. app/schemas/__init__.py - Tüm şemaları import et
```

**Test Scripti:**
```python
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
            "script_token": str(uuid4())
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
            "created_at": datetime.now()
        }
        conversation_list = ConversationList(**conversation_list_data)
        print("OK ConversationList schema dogru calisiyor")
        
        # ConversationStats test
        conversation_stats_data = {
            "total_conversations": 100,
            "avg_latency": 200,
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
        
        # PaginationResponse test
        pagination_response_data = {
            "items": [],
            "total": 0,
            "page": 1,
            "size": 10,
            "pages": 0
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
```

**Hata Çözme Promtu:**
```python
# Olası hatalar ve çözümleri:

1. "Schema import hatası":
   - app/schemas/__init__.py dosyasında import'lar doğru mu?
   - Tüm schema dosyaları oluşturuldu mu?
   - Circular import var mı? TYPE_CHECKING kullan

2. "Field validation hatası":
   - Optional field'lar doğru tanımlandı mı?
   - Response schema'ları model'lerden farklı field'lar içerebilir
   - Alias kullanarak field name mapping yap

3. "Model vs Schema karışıklığı":
   - Model: Veritabanı yapısı (internal)
   - Schema: API input/output yapısı (external)
   - Schema'lar bazı field'ları gizler, bazılarını ekler

4. "Pagination schema sorunları":
   - Generic typing kullan: PaginationResponse[T]
   - items field'ı List[Any] olmalı
   - total, page, size, pages field'ları gerekli

5. "Response schema eksik field'lar":
   - API'nin döndüğü tüm field'lar Response schema'da olmalı
   - created_at, updated_at gibi timestamp'ler ekle
   - Relation field'ları için nested schema'lar kullan

6. "Update schema validation":
   - Tüm field'lar Optional olmalı (kısmi güncelleme için)
   - id, created_at gibi field'lar Update schema'da olmamalı
   - Validation rules (min_length, pattern) ekle

7. "Public schema güvenlik":
   - Sensitive field'ları Public schema'larda gösterme
   - script_token, user_id gibi bilgiler dikkatli paylaş
   - Widget için minimal bilgi set'i kullan

8. "Stats schema veri tipleri":
   - Sayısal field'lar için doğru tip (int, float)
   - Dict field'lar için typing tanımla
   - Optional field'lar için default value ekle

9. "Chat widget schema format":
   - Frontend ile uyumlu field name'ler kullan
   - Timestamp format'ı tutarlı olsun (ISO format)
   - message, is_user field'ları gerekli

10. "Common schema reusability":
    - StatusResponse gibi ortak schema'ları tekrar kullan
    - Error handling için tutarlı format
    - Pagination için generic approach kullan
```

### ✅ 9. API Router'ları
- [X] `app/routers/brands.py` - Marka yönetimi endpoint'leri
- [X] `app/routers/chatbots.py` - Chatbot yönetimi endpoint'leri
- [X] `app/routers/knowledge.py` - Bilgi kaynakları endpoint'leri  
- [X] `app/routers/conversations.py` - Konuşma endpoint'leri
- [X] `app/routers/uploads.py` - Dosya yükleme endpoint'leri
- [X] `app/routers/widget.py` - Widget endpoint'leri
- [X] `app/routers/feedback.py` - Geri bildirim endpoint'leri

### ✅ 10. Temel Servisleri
- [ ] `app/services/chatbot_service.py` - Chatbot iş mantığı
- [ ] `app/services/embedding_service.py` - AI/Embedding işlemleri (opsiyonel)

## 📦 Requirements.txt İçeriği

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
python-multipart==0.0.6
supabase==2.2.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dateutil==2.8.2
requests==2.31.0
openai==1.3.0
```

## 🔧 Konfigürasyon Dosyaları

### .env.example
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# JWT Configuration
SECRET_KEY=your_super_secret_jwt_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

# OpenRouter Configuration (for AI models)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

## 🗄️ Supabase Tablo Oluşturma SQL'leri

Bu SQL komutlarını Supabase Dashboard > SQL Editor'da çalıştırın:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (Supabase Auth ile otomatik oluşur, genişletilmeli)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Brands table
CREATE TABLE IF NOT EXISTS public.brands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    logo_url TEXT,
    theme_color TEXT DEFAULT '#3B82F6',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chatbots table
CREATE TABLE IF NOT EXISTS public.chatbots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID NOT NULL REFERENCES public.brands(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    avatar_url TEXT,
    primary_color TEXT DEFAULT '#3B82F6',
    secondary_color TEXT DEFAULT '#EF4444',
    animation_style TEXT DEFAULT 'fade',
    script_token TEXT UNIQUE NOT NULL DEFAULT uuid_generate_v4()::TEXT,
    language TEXT DEFAULT 'tr',
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge base entries table
CREATE TABLE IF NOT EXISTS public.knowledge_base_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatbot_id UUID NOT NULL REFERENCES public.chatbots(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,
    source_url TEXT,
    content TEXT,
    embedding_id TEXT,
    token_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat prompts table
CREATE TABLE IF NOT EXISTS public.chat_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatbot_id UUID NOT NULL REFERENCES public.chatbots(id) ON DELETE CASCADE,
    prompt_text TEXT NOT NULL,
    temperature FLOAT DEFAULT 0.7,
    context_size INTEGER DEFAULT 2000,
    top_p FLOAT DEFAULT 0.9,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations table
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatbot_id UUID NOT NULL REFERENCES public.chatbots(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL,
    user_input TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    source_entry_id UUID REFERENCES public.knowledge_base_entries(id),
    latency_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feedback table
CREATE TABLE IF NOT EXISTS public.feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Uploads table
CREATE TABLE IF NOT EXISTS public.uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatbot_id UUID NOT NULL REFERENCES public.chatbots(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    storage_url TEXT NOT NULL,
    processed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_brands_user_id ON public.brands(user_id);
CREATE INDEX IF NOT EXISTS idx_chatbots_brand_id ON public.chatbots(brand_id);
CREATE INDEX IF NOT EXISTS idx_chatbots_script_token ON public.chatbots(script_token);
CREATE INDEX IF NOT EXISTS idx_knowledge_chatbot_id ON public.knowledge_base_entries(chatbot_id);
CREATE INDEX IF NOT EXISTS idx_conversations_chatbot_id ON public.conversations(chatbot_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON public.conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_uploads_chatbot_id ON public.uploads(chatbot_id);
```

## 🚀 İlk Çalıştırma Adımları

### 1. Sanal Ortam Oluştur ve Aktive Et
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 2. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 3. Ortam Değişkenlerini Ayarla
```bash
cp .env.example .env
# .env dosyasını düzenleyip Supabase bilgilerinizi ekleyin
```

### 4. Uygulamayı Çalıştır
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. API Dokümantasyonunu Kontrol Et
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 İlk Test Endpoint'leri

Kurulum tamamlandığında şu endpoint'ler çalışır durumda olacak:

- `GET /` - Health check
- `GET /me` - Kullanıcı profili (JWT gerekli)
- `GET /brands/` - Kullanıcının markaları (JWT gerekli)
- `POST /brands/` - Yeni marka oluştur (JWT gerekli)
- `GET /chatbots/` - Kullanıcının chatbot'ları (JWT gerekli)
- `POST /chatbots/` - Yeni chatbot oluştur (JWT gerekli)

## 📝 Önemli Notlar

1. **Supabase Konfigürasyonu**: .env dosyasında Supabase URL ve Key'leri doğru şekilde ayarlayın
2. **JWT Secret**: SECRET_KEY'i güvenli bir değer ile değiştirin
3. **CORS**: Frontend'in çalışacağı domain'i CORS ayarlarına ekleyin
4. **Veritabanı**: SQL komutlarını Supabase'de çalıştırmayı unutmayın
5. **Dependencies**: Virtual environment kullanmayı unutmayın

Bu adımları tamamladığınızda temel seviyede çalışan MarkaMind FastAPI backend'iniz hazır olacak!