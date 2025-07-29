# MarkaMind Platform - Görev Tabanlı Geliştirme Yol Haritası (PRD)

## 📋 Proje Genel Bakış

MarkaMind, markalara özel yapay zeka destekli chatbot geliştirme platformudur. Bu PRD, her görevi checkbox sistemi ile takip edilebilir şekilde organize eder ve her görev için detaylı implementation ve test prompts sağlar.

### 🎯 Platform Vizyonu
- **No-code** chatbot oluşturma deneyimi  
- **RAG (Retrieval-Augmented Generation)** ile markaya özel AI eğitimi
- **Sanal mağaza** ortamında test edilebilir chatbot'lar
- **50+ animasyon** ile görsel özelleştirme
- **Gelişmiş analitik** ve performans takibi

---

## 🗓️ GÖREV TABANLI DEVELOPMENT ROADMAP

### PHASE 1: FOUNDATION & CORE BACKEND (Hafta 1-4)

## GÖREV 1.1: PROJECT SETUP & INFRASTRUCTURE 🔧

### Ana Görev Listesi:
- [ ] **1.1.1** - Proje dizin yapısı oluşturma
- [ ] **1.1.2** - Virtual environment kurulumu  
- [ ] **1.1.3** - Dependencies yükleme
- [ ] **1.1.4** - Core configuration dosyaları
- [ ] **1.1.5** - Docker containerization

### Alt Görev 1.1.1: Proje Dizin Yapısı Oluşturma

**Etkilenen Dosyalar:**
- `fastapi-architecture.md` (klasör yapısı referansı)

**Implementation Prompt:**
```
"FastAPI projesi için temel klasör yapısını oluştur. fastapi-architecture.md'deki yapıyı takip et. 
app/ klasörü içinde models/, schemas/, api/, services/, repositories/, core/, config/, tasks/ 
klasörlerini oluştur ve her klasörde __init__.py ekle."
```

**Test Script:** `tests/test_project_structure.py`
**Test Prompt:**
```
"Project structure test dosyası oluştur. Tüm klasörlerin ve __init__.py dosyalarının varlığını kontrol et."
```

**Error Handling:**
- **"Directory already exists"** → `"mkdir -p komutu ile güvenli klasör oluştur"`
- **"Permission denied"** → `"chmod/sudo ile yazma izni ver"`

---

## GÖREV 1.2: DATABASE MODELS & AUTHENTICATION 🗄️

### Ana Görev Listesi:
- [ ] **1.2.1** - SQLAlchemy base model oluşturma
- [ ] **1.2.2** - User model implementasyonu
- [ ] **1.2.3** - Chatbot model implementasyonu
- [ ] **1.2.4** - Authentication sistem kurulumu
- [ ] **1.2.5** - Alembic migration setup

### Alt Görev 1.2.1: SQLAlchemy Base Model Oluşturma

**Etkilenen Dosyalar:**
- `database-schema.md` (model yapısı)
- `fastapi-architecture.md` (base model pattern)

**Implementation Prompt:**
```
"database-schema.md'deki BaseModel yapısını takip ederek app/models/base.py oluştur.
SQLAlchemy DeclarativeMeta kullan, id, created_at, updated_at field'ları ekle.
UUID primary key support ekle."
```

**Test Script:** `tests/test_models/test_base_model.py`
**Test Prompt:**
```
"Base model test dosyası oluştur. Model inheritance, UUID generation, 
timestamp fields'ı test et."
```

**Error Handling:**
- **"SQLAlchemy import error"** → `"sqlalchemy dependency'i kontrol et"`
- **"UUID generation fails"** → `"uuid4 import'unu ve PostgreSQL extension'ını kontrol et"`

### Alt Görev 1.2.2: User Model Implementasyonu

**Etkilenen Dosyalar:**
- `database-schema.md` (users tablosu)
- `authentication-security.md` (user fields)

**Implementation Prompt:**
```
"database-schema.md'deki users tablosunu SQLAlchemy model olarak app/models/user.py'da oluştur.
BaseModel'den inherit et, email, password_hash, first_name, last_name, company_name fields ekle.
Email uniqueness ve indexleri dahil et."
```

**Test Script:** `tests/test_models/test_user_model.py`
**Test Prompt:**
```
"User model test dosyası oluştur. User creation, email uniqueness, 
password hashing, field validations test et."
```

**Error Handling:**
- **"Email constraint violation"** → `"Email uniqueness kontrolü ekle"`
- **"Password hashing fails"** → `"passlib dependency ve bcrypt algoritması kontrol et"`

### Alt Görev 1.2.3: Chatbot Model Implementasyonu

**Etkilenen Dosyalar:**
- `database-schema.md` (chatbots tablosu)
- `endpoint.md` (chatbot fields)

**Implementation Prompt:**
```
"database-schema.md'deki chatbots tablosunu SQLAlchemy model olarak app/models/chatbot.py'da oluştur.
User ile ForeignKey relationship kur, name, description, settings (JSONB), appearance (JSONB) fields ekle.
Status enum (draft, active, inactive, training) ekle."
```

**Test Script:** `tests/test_models/test_chatbot_model.py`
**Test Prompt:**
```
"Chatbot model test dosyası oluştur. Chatbot-User relationship, 
JSONB fields, status transitions, validation test et."
```

**Error Handling:**
- **"JSONB not supported"** → `"PostgreSQL kullandığınızdan emin ol"`
- **"Foreign key constraint"** → `"User model'in create edildiğini kontrol et"`

### Alt Görev 1.2.4: Authentication Sistem Kurulumu

**Etkilenen Dosyalar:**
- `authentication-security.md` (JWT implementation)
- `third-party-integrations.md` (Supabase auth)

**Implementation Prompt:**
```
"authentication-security.md'deki JWT implementasyonunu app/core/security.py'da oluştur.
create_access_token, verify_password, get_password_hash, get_current_user fonksiyonları implement et.
Supabase Auth entegrasyonu ekle."
```

**Test Script:** `tests/test_core/test_security.py`
**Test Prompt:**
```
"Security test dosyası oluştur. JWT token creation/validation, 
password hashing/verification, user authentication test et."
```

**Error Handling:**
- **"JWT decode error"** → `"SECRET_KEY ve ALGORITHM settings'i kontrol et"`
- **"Supabase connection error"** → `"SUPABASE_URL ve KEY'leri kontrol et"`

### Alt Görev 1.2.5: Alembic Migration Setup

**Etkilenen Dosyalar:**
- `database-schema.md` (migration strategy)

**Implementation Prompt:**
```
"Alembic migration setup yap. alembic init alembic komutu çalıştır.
database-schema.md'deki 8 aşamalı migration planını takip et.
Initial migration oluştur: alembic revision --autogenerate -m 'Initial tables'"
```

**Test Script:** `tests/test_migrations/test_alembic.py`
**Test Prompt:**
```
"Alembic test dosyası oluştur. Migration generation, upgrade/downgrade, 
version tracking test et."
```

**Error Handling:**
- **"Migration conflict"** → `"Alembic version history'i kontrol et"`
- **"Database connection error"** → `"DATABASE_URL ve PostgreSQL connection'ı kontrol et"`

---

## GÖREV 1.3: CORE API DEVELOPMENT 🌐

### Ana Görev Listesi:
- [ ] **1.3.1** - Repository pattern implementasyonu
- [ ] **1.3.2** - Service layer geliştirme
- [ ] **1.3.3** - Authentication endpoints
- [ ] **1.3.4** - User management endpoints
- [ ] **1.3.5** - Chatbot CRUD endpoints

### Alt Görev 1.3.1: Repository Pattern Implementasyonu

**Etkilenen Dosyalar:**
- `fastapi-architecture.md` (BaseRepository pattern)

**Implementation Prompt:**
```
"fastapi-architecture.md'deki BaseRepository pattern'ini app/repositories/base.py'da oluştur.
Generic typing kullan, CRUD operations (get, get_multi, create, update, delete) implement et.
SQLAlchemy session management ekle."
```

**Test Script:** `tests/test_repositories/test_base_repository.py`
**Test Prompt:**
```
"Base repository test dosyası oluştur. CRUD operations, 
generic typing, session management test et."
```

**Error Handling:**
- **"Generic typing error"** → `"Python 3.9+ kullandığınızdan emin ol"`
- **"Session management error"** → `"Database session factory'i kontrol et"`

### Alt Görev 1.3.2: Service Layer Geliştirme

**Etkilenen Dosyalar:**
- `fastapi-architecture.md` (service layer architecture)

**Implementation Prompt:**
```
"fastapi-architecture.md'deki service layer pattern'ini takip ederek:
- app/services/user_service.py (user business logic)  
- app/services/chatbot_service.py (chatbot business logic)
- app/services/auth_service.py (authentication logic)
oluştur. Repository'leri inject et."
```

**Test Script:** `tests/test_services/`
**Test Prompt:**
```
"Service layer test dosyaları oluştur. Business logic, 
repository interactions, error handling test et."
```

**Error Handling:**
- **"Dependency injection error"** → `"FastAPI Depends kullanımını kontrol et"`
- **"Business validation fails"** → `"Service layer validation rules'ları kontrol et"`

### Alt Görev 1.3.3: Authentication Endpoints

**Etkilenen Dosyalar:**
- `endpoint.md` (authentication endpoints)
- `authentication-security.md` (security implementation)

**Implementation Prompt:**
```
"endpoint.md'deki authentication endpoint'lerini app/api/v1/endpoints/auth.py'da implement et:
- POST /auth/register (user registration)
- POST /auth/login (user login)  
- POST /auth/refresh (token refresh)
- POST /auth/logout (logout)
FastAPI router kullan, Pydantic schemas ile validation ekle."
```

**Test Script:** `tests/test_api/test_auth_endpoints.py`
**Test Prompt:**
```
"Authentication endpoints test dosyası oluştur. Registration, login, 
token refresh, logout flows test et. FastAPI TestClient kullan."
```

**Error Handling:**
- **"Validation error"** → `"Pydantic schema'ları kontrol et"`
- **"Authentication fails"** → `"JWT token generation/validation kontrol et"`

### Alt Görev 1.3.4: User Management Endpoints

**Etkilenen Dosyalar:**
- `endpoint.md` (user management endpoints)

**Implementation Prompt:**
```
"endpoint.md'deki user management endpoint'lerini app/api/v1/endpoints/users.py'da implement et:
- GET /users/me (current user profile)
- PUT /users/me (update profile)
- DELETE /users/me (delete account)
- POST /users/change-password (password change)
Authentication required endpoints ekle."
```

**Test Script:** `tests/test_api/test_user_endpoints.py`
**Test Prompt:**
```
"User management endpoints test dosyası oluştur. Profile operations,
authentication requirements, authorization test et."
```

**Error Handling:**
- **"Authorization error"** → `"JWT token ve user permissions kontrol et"`
- **"Profile update fails"** → `"User model validations kontrol et"`

### Alt Görev 1.3.5: Chatbot CRUD Endpoints

**Etkilenen Dosyalar:**
- `endpoint.md` (chatbot endpoints)

**Implementation Prompt:**
```
"endpoint.md'deki chatbot CRUD endpoint'lerini app/api/v1/endpoints/chatbots.py'da implement et:
- GET /chatbots (list user chatbots)
- POST /chatbots (create chatbot)
- GET /chatbots/{chatbot_id} (get chatbot)
- PUT /chatbots/{chatbot_id} (update chatbot)
- DELETE /chatbots/{chatbot_id} (delete chatbot)
User authorization ve ownership kontrolü ekle."
```

**Test Script:** `tests/test_api/test_chatbot_endpoints.py`
**Test Prompt:**
```
"Chatbot CRUD endpoints test dosyası oluştur. CRUD operations,
user ownership, authorization test et."
```

**Error Handling:**
- **"Ownership violation"** → `"User-Chatbot relationship kontrolü ekle"`
- **"Chatbot not found"** → `"404 error handling implement et"`

---

## GÖREV 1.4: THIRD-PARTY INTEGRATIONS 🔌

### Ana Görev Listesi:
- [ ] **1.4.1** - OpenRouter API client implementasyonu
- [ ] **1.4.2** - Supabase integration setup
- [ ] **1.4.3** - Email service kurulumu
- [ ] **1.4.4** - File storage implementasyonu
- [ ] **1.4.5** - Redis caching setup

### Alt Görev 1.4.1: OpenRouter API Client Implementasyonu

**Etkilenen Dosyalar:**
- `third-party-integrations.md` (OpenRouter client)

**Implementation Prompt:**
```
"third-party-integrations.md'deki OpenRouterClient class'ını app/integrations/openrouter/client.py'da oluştur.
create_completion, create_embedding, stream_completion, get_available_models fonksiyonları implement et.
Error handling ve retry logic ekle."
```

**Test Script:** `tests/test_integrations/test_openrouter.py`
**Test Prompt:**
```
"OpenRouter client test dosyası oluştur. API calls, error handling,
retry logic, model selection test et. Mock responses kullan."
```

**Error Handling:**
- **"API key invalid"** → `"OPENROUTER_API_KEY settings'i kontrol et"`
- **"Rate limit exceeded"** → `"Retry logic ve exponential backoff ekle"`

### Alt Görev 1.4.2: Supabase Integration Setup

**Etkilenen Dosyalar:**
- `third-party-integrations.md` (Supabase configuration)

**Implementation Prompt:**
```
"third-party-integrations.md'deki SupabaseClient'ı app/integrations/supabase/client.py'da implement et.
Database connection, authentication, file storage, real-time subscriptions fonksiyonları ekle.
Row Level Security (RLS) policies setup."
```

**Test Script:** `tests/test_integrations/test_supabase.py`
**Test Prompt:**
```
"Supabase integration test dosyası oluştur. Auth, database, storage,
RLS policies test et."
```

**Error Handling:**
- **"Supabase connection fails"** → `"SUPABASE_URL ve credentials kontrol et"`
- **"RLS policy violation"** → `"Database policies ve user context kontrol et"`

### Alt Görev 1.4.3: Email Service Kurulumu

**Etkilenen Dosyalar:**
- `third-party-integrations.md` (email service)

**Implementation Prompt:**
```
"third-party-integrations.md'deki EmailService'i app/services/email_service.py'da oluştur.
SMTP, SendGrid provider support ekle. Template-based email system implement et.
Welcome, verification, password reset email templates oluştur."
```

**Test Script:** `tests/test_services/test_email_service.py`
**Test Prompt:**
```
"Email service test dosyası oluştur. SMTP connection, template rendering,
email sending test et. Mock SMTP server kullan."
```

**Error Handling:**
- **"SMTP connection error"** → `"SMTP settings ve credentials kontrol et"`
- **"Template rendering fails"** → `"Jinja2 template syntax kontrol et"`

### Alt Görev 1.4.4: File Storage Implementasyonu

**Etkilenen Dosyalar:**
- `third-party-integrations.md` (file storage)

**Implementation Prompt:**
```
"third-party-integrations.md'deki file storage system'i implement et.
Multi-provider support (Supabase Storage, Local Storage) ekle.
File validation, upload, download, delete operations implement et."
```

**Test Script:** `tests/test_services/test_file_service.py`
**Test Prompt:**
```
"File service test dosyası oluştur. File upload/download, validation,
provider switching test et."
```

**Error Handling:**
- **"File upload fails"** → `"File size limits ve permissions kontrol et"`
- **"Storage provider error"** → `"Provider credentials ve configuration kontrol et"`

### Alt Görev 1.4.5: Redis Caching Setup

**Etkilenen Dosyalar:**
- `analytics-implementation.md` (caching strategy)

**Implementation Prompt:**
```
"Redis caching client setup yap. app/core/cache.py oluştur.
Cache get/set/delete operations, TTL management, key patterns implement et.
Session storage ve analytics caching için use cases ekle."
```

**Test Script:** `tests/test_core/test_cache.py`
**Test Prompt:**
```
"Redis cache test dosyası oluştur. Cache operations, TTL, 
key patterns test et. Redis mock kullan."
```

**Error Handling:**
- **"Redis connection error"** → `"REDIS_URL ve Redis server status kontrol et"`
- **"Cache serialization error"** → `"JSON serialization ve complex objects kontrol et"`

---

## GÖREV 2.1: RAG SYSTEM CORE 🧠

### Ana Görev Listesi:
- [ ] **2.1.1** - Text processing pipeline
- [ ] **2.1.2** - Embedding generation system
- [ ] **2.1.3** - Vector database setup (ChromaDB)
- [ ] **2.1.4** - Similarity search implementation
- [ ] **2.1.5** - RAG service integration

### Alt Görev 2.1.1: Text Processing Pipeline

**Etkilenen Dosyalar:**
- `rag-system.md` (text processing)

**Implementation Prompt:**
```
"rag-system.md'deki text processing pipeline'ını app/services/text_processor.py'da implement et.
PDF text extraction (PyPDF2), text chunking (1000 char, 200 overlap), 
content preprocessing ve metadata extraction fonksiyonları ekle."
```

**Test Script:** `tests/test_services/test_text_processor.py`
**Test Prompt:**
```
"Text processor test dosyası oluştur. PDF extraction, chunking algorithm,
preprocessing quality test et. Sample PDF files kullan."
```

**Error Handling:**
- **"PDF parsing error"** → `"PDF file integrity ve PyPDF2 compatibility kontrol et"`
- **"Text encoding issues"** → `"UTF-8 encoding ve special characters handling ekle"`

### Alt Görev 2.1.2: Embedding Generation System

**Etkilenen Dosyalar:**
- `rag-system.md` (embedding implementation)
- `third-party-integrations.md` (OpenRouter embeddings)

**Implementation Prompt:**
```
"rag-system.md'deki embedding system'i app/services/embedding_service.py'da implement et.
OpenRouter text-embedding-ada-002 model kullan, batch processing, 
error handling ve cost tracking ekle."
```

**Test Script:** `tests/test_services/test_embedding_service.py`
**Test Prompt:**
```
"Embedding service test dosyası oluştur. Embedding generation, batch processing,
cost calculation test et. OpenRouter API mock kullan."
```

**Error Handling:**
- **"Embedding API error"** → `"OpenRouter API key ve rate limits kontrol et"`
- **"Batch processing fails"** → `"Token limits ve batch size optimization kontrol et"`

### Alt Görev 2.1.3: Vector Database Setup (ChromaDB)

**Etkilenen Dosyalar:**
- `rag-system.md` (ChromaDB configuration)

**Implementation Prompt:**
```
"rag-system.md'deki ChromaDB setup'ını app/integrations/chromadb/client.py'da implement et.
Collection management, embedding storage, index optimization fonksiyonları ekle.
Chatbot bazında collection isolation sağla."
```

**Test Script:** `tests/test_integrations/test_chromadb.py`
**Test Prompt:**
```
"ChromaDB test dosyası oluştur. Collection operations, embedding storage,
query performance test et."
```

**Error Handling:**
- **"ChromaDB connection error"** → `"ChromaDB installation ve persistence path kontrol et"`
- **"Collection creation fails"** → `"Disk space ve permissions kontrol et"`

### Alt Görev 2.1.4: Similarity Search Implementation

**Etkilenen Dosyalar:**
- `rag-system.md` (similarity search)

**Implementation Prompt:**
```
"rag-system.md'deki similarity search'ü app/services/search_service.py'da implement et.
Cosine similarity, top-k retrieval, similarity threshold filtering,
metadata-based filtering fonksiyonları ekle."
```

**Test Script:** `tests/test_services/test_search_service.py`
**Test Prompt:**
```
"Search service test dosyası oluştur. Similarity calculations, 
filtering, ranking test et."
```

**Error Handling:**
- **"Low similarity scores"** → `"Embedding quality ve similarity threshold ayarlarını kontrol et"`
- **"Search performance issues"** → `"Index optimization ve query parameters kontrol et"`

### Alt Görev 2.1.5: RAG Service Integration

**Etkilenen Dosyalar:**
- `rag-system.md` (RAG service)

**Implementation Prompt:**
```
"rag-system.md'deki RAGService class'ını app/services/rag_service.py'da implement et.
process_training_data, semantic_search, generate_response fonksiyonları ekle.
End-to-end RAG pipeline oluştur."
```

**Test Script:** `tests/test_services/test_rag_service.py`
**Test Prompt:**
```
"RAG service test dosyası oluştur. End-to-end pipeline, 
context generation, response quality test et."
```

**Error Handling:**
- **"Context too long"** → `"Context truncation ve summarization ekle"`
- **"RAG response quality low"** → `"Retrieval parameters ve prompt engineering optimize et"`

---

## GÖREV 2.2: TRAINING DATA MANAGEMENT 📚

### Ana Görev Listesi:
- [ ] **2.2.1** - Training data API endpoints
- [ ] **2.2.2** - File upload ve validation
- [ ] **2.2.3** - Background processing (Celery)
- [ ] **2.2.4** - Progress tracking system
- [ ] **2.2.5** - Data quality monitoring

### Alt Görev 2.2.1: Training Data API Endpoints

**Etkilenen Dosyalar:**
- `endpoint.md` (training endpoints)

**Implementation Prompt:**
```
"endpoint.md'deki training data endpoint'lerini app/api/v1/endpoints/training.py'da implement et:
- POST /training/upload (file upload)
- GET /training/{chatbot_id} (list training data)
- DELETE /training/{data_id} (delete training data)
- POST /training/{chatbot_id}/retrain (trigger retraining)
File upload handling ve multipart form data support ekle."
```

**Test Script:** `tests/test_api/test_training_endpoints.py`
**Test Prompt:**
```
"Training endpoints test dosyası oluştur. File upload, data management,
retraining triggers test et."
```

**Error Handling:**
- **"File upload timeout"** → `"Upload timeout settings ve chunk upload implement et"`
- **"Invalid file format"** → `"File type validation ve supported formats kontrol et"`

### Alt Görev 2.2.2: File Upload ve Validation

**Etkilenen Dosyalar:**
- `third-party-integrations.md` (file service)

**Implementation Prompt:**
```
"File upload validation system'i app/services/file_validator.py'da implement et.
File size limits (50MB), supported formats (PDF, TXT, DOCX), 
content validation, malware scanning ekle."
```

**Test Script:** `tests/test_services/test_file_validator.py`
**Test Prompt:**
```
"File validator test dosyası oluştur. Size limits, format validation,
security checks test et."
```

**Error Handling:**
- **"File too large"** → `"Chunk upload ve compression options implement et"`
- **"Malicious file detected"** → `"File scanning services ve quarantine implement et"`

### Alt Görev 2.2.3: Background Processing (Celery)

**Etkilenen Dosyalar:**
- `fastapi-architecture.md` (Celery configuration)

**Implementation Prompt:**
```
"fastapi-architecture.md'deki Celery configuration'ı setup et.
app/tasks/celery_app.py ve app/tasks/training_tasks.py oluştur.
File processing, embedding generation, retraining tasks implement et."
```

**Test Script:** `tests/test_tasks/test_training_tasks.py`
**Test Prompt:**
```
"Celery tasks test dosyası oluştur. Task execution, retry logic,
error handling test et."
```

**Error Handling:**
- **"Celery worker not available"** → `"Redis broker ve worker status kontrol et"`
- **"Task timeout"** → `"Task timeout settings ve chunk processing implement et"`

### Alt Görev 2.2.4: Progress Tracking System

**Etkilenen Dosyalar:**
- `analytics-implementation.md` (progress tracking)

**Implementation Prompt:**
```
"Training progress tracking system'i app/services/progress_service.py'da implement et.
Real-time progress updates, WebSocket notifications, 
progress persistence implement et."
```

**Test Script:** `tests/test_services/test_progress_service.py`
**Test Prompt:**
```
"Progress service test dosyası oluştur. Progress tracking, 
WebSocket updates, persistence test et."
```

**Error Handling:**
- **"Progress updates missing"** → `"WebSocket connection ve Redis pub/sub kontrol et"`
- **"Progress calculation error"** → `"Task step counting ve percentage calculation kontrol et"`

### Alt Görev 2.2.5: Data Quality Monitoring

**Etkilenen Dosyalar:**
- `rag-system.md` (quality metrics)

**Implementation Prompt:**
```
"Data quality monitoring system'i app/services/quality_service.py'da implement et.
Content quality scoring, duplicate detection, 
training data health metrics implement et."
```

**Test Script:** `tests/test_services/test_quality_service.py`
**Test Prompt:**
```
"Quality service test dosyası oluştur. Quality scoring, 
duplicate detection, health metrics test et."
```

**Error Handling:**
- **"Quality score calculation fails"** → `"Text analysis algorithms ve metrics kontrol et"`
- **"Duplicate detection inaccurate"** → `"Similarity thresholds ve hashing algorithms optimize et"`

---

## GÖREV 2.3: CHAT SYSTEM IMPLEMENTATION 💬

### Ana Görev Listesi:
- [ ] **2.3.1** - Conversation management
- [ ] **2.3.2** - Message handling system
- [ ] **2.3.3** - RAG-enhanced response generation
- [ ] **2.3.4** - WebSocket real-time messaging
- [ ] **2.3.5** - Response streaming

### Alt Görev 2.3.1: Conversation Management

**Etkilenen Dosyalar:**
- `endpoint.md` (chat endpoints)
- `database-schema.md` (conversations table)

**Implementation Prompt:**
```
"Conversation management system'i implement et:
- app/models/conversation.py (conversation model)
- app/services/conversation_service.py (conversation logic)
- app/api/v1/endpoints/conversations.py (conversation endpoints)
Session handling, conversation state, context management ekle."
```

**Test Script:** `tests/test_services/test_conversation_service.py`
**Test Prompt:**
```
"Conversation service test dosyası oluştur. Conversation lifecycle,
state management, context handling test et."
```

**Error Handling:**
- **"Session expired"** → `"Session timeout ve renewal mechanism implement et"`
- **"Context too large"** → `"Context truncation ve summarization implement et"`

### Alt Görev 2.3.2: Message Handling System

**Etkilenen Dosyalar:**
- `database-schema.md` (messages table)

**Implementation Prompt:**
```
"Message handling system'i implement et:
- app/models/message.py (message model)
- app/services/message_service.py (message logic)
Message types (user, bot, system), metadata, response time tracking ekle."
```

**Test Script:** `tests/test_services/test_message_service.py`
**Test Prompt:**
```
"Message service test dosyası oluştur. Message creation, 
type handling, metadata tracking test et."
```

**Error Handling:**
- **"Message validation fails"** → `"Content validation rules ve sanitization kontrol et"`
- **"Response time tracking inaccurate"** → `"Timestamp precision ve calculation methods kontrol et"`

### Alt Görev 2.3.3: RAG-Enhanced Response Generation

**Etkilenen Dosyalar:**
- `rag-system.md` (response generation)

**Implementation Prompt:**
```
"RAG-enhanced response generation'ı app/services/response_service.py'da implement et.
Context retrieval, prompt engineering, response generation,
confidence scoring ve source attribution ekle."
```

**Test Script:** `tests/test_services/test_response_service.py`
**Test Prompt:**
```
"Response service test dosyası oluştur. RAG pipeline, 
response quality, confidence scoring test et."
```

**Error Handling:**
- **"Low confidence responses"** → `"RAG parameters ve prompt templates optimize et"`
- **"Response generation timeout"** → `"OpenRouter timeout settings ve fallback responses ekle"`

### Alt Görev 2.3.4: WebSocket Real-time Messaging

**Etkilenen Dosyalar:**
- `analytics-implementation.md` (WebSocket implementation)

**Implementation Prompt:**
```
"WebSocket real-time messaging'i app/api/v1/websocket/chat.py'da implement et.
Connection management, message broadcasting, typing indicators,
connection recovery implement et."
```

**Test Script:** `tests/test_websocket/test_chat_websocket.py`
**Test Prompt:**
```
"WebSocket test dosyası oluştur. Connection handling, 
message broadcasting, recovery test et."
```

**Error Handling:**
- **"WebSocket connection drops"** → `"Connection retry ve heartbeat mechanism implement et"`
- **"Message delivery fails"** → `"Message queuing ve retry logic implement et"`

### Alt Görev 2.3.5: Response Streaming

**Etkilenen Dosyalar:**
- `third-party-integrations.md` (streaming responses)

**Implementation Prompt:**
```
"Response streaming'i implement et. OpenRouter streaming API kullan,
real-time response chunks, typing indicators,
stream error handling ekle."
```

**Test Script:** `tests/test_services/test_streaming_service.py`
**Test Prompt:**
```
"Streaming service test dosyası oluştur. Stream handling, 
chunk processing, error recovery test et."
```

**Error Handling:**
- **"Stream interruption"** → `"Stream recovery ve partial response handling implement et"`
- **"Chunk ordering issues"** → `"Sequence tracking ve reassembly implement et"`

---

## GÖREV 3.1: FRONTEND FOUNDATION (NEXT.JS) ⚛️

### Ana Görev Listesi:
- [ ] **3.1.1** - Next.js 14 project setup
- [ ] **3.1.2** - TypeScript configuration
- [ ] **3.1.3** - Tailwind CSS design system
- [ ] **3.1.4** - Authentication integration
- [ ] **3.1.5** - API client setup

### Alt Görev 3.1.1: Next.js 14 Project Setup

**Etkilenen Dosyalar:**
- Yeni Next.js projesi

**Implementation Prompt:**
```
"Next.js 14 projesi oluştur:
npx create-next-app@latest markamind-frontend --typescript --tailwind --app
App Router, TypeScript, Tailwind CSS ile setup yap.
Folder structure: app/, components/, hooks/, utils/, types/ oluştur."
```

**Test Script:** `__tests__/setup.test.tsx`
**Test Prompt:**
```
"Next.js setup test dosyası oluştur. Project structure, 
TypeScript config, Tailwind CSS loading test et."
```

**Error Handling:**
- **"Next.js installation fails"** → `"Node.js version (18+) ve npm cache kontrol et"`
- **"App Router issues"** → `"Next.js 13+ App Router migration guide takip et"`

### Alt Görev 3.1.2: TypeScript Configuration

**Implementation Prompt:**
```
"TypeScript configuration optimize et:
- tsconfig.json strict mode enable
- Path aliases (@/ for src/, @components/ for components/)
- Type definitions oluştur (types/index.ts)
- API response types tanımla"
```

**Test Script:** `__tests__/typescript.test.ts`
**Test Prompt:**
```
"TypeScript config test dosyası oluştur. Type checking, 
path aliases, strict mode compliance test et."
```

**Error Handling:**
- **"TypeScript errors"** → `"Type definitions ve import paths kontrol et"`
- **"Path alias resolution fails"** → `"tsconfig.json paths configuration kontrol et"`

### Alt Görev 3.1.3: Tailwind CSS Design System

**Implementation Prompt:**
```
"Tailwind CSS design system setup:
- tailwind.config.js custom theme
- Design tokens (colors, typography, spacing)
- Component library (Button, Input, Card, Modal)
- Responsive design utilities"
```

**Test Script:** `__tests__/design-system.test.tsx`
**Test Prompt:**
```
"Design system test dosyası oluştur. Component rendering, 
theme consistency, responsive behavior test et."
```

**Error Handling:**
- **"Tailwind classes not working"** → `"PostCSS config ve CSS import paths kontrol et"`
- **"Design token inconsistency"** → `"Tailwind config theme extension kontrol et"`

### Alt Görev 3.1.4: Authentication Integration

**Implementation Prompt:**
```
"Authentication system integrate et:
- Supabase Auth client setup
- useAuth hook oluştur
- Protected routes middleware
- Login/Register forms
- JWT token management"
```

**Test Script:** `__tests__/auth.test.tsx`
**Test Prompt:**
```
"Authentication test dosyası oluştur. Login/logout flows, 
protected routes, token management test et."
```

**Error Handling:**
- **"Supabase auth fails"** → `"Supabase credentials ve client initialization kontrol et"`
- **"Protected route bypass"** → `"Middleware authentication checks kontrol et"`

### Alt Görev 3.1.5: API Client Setup

**Implementation Prompt:**
```
"API client setup:
- Axios/Fetch client configuration
- Base URL ve interceptors
- Error handling middleware
- Type-safe API calls
- Request/Response interfaces"
```

**Test Script:** `__tests__/api-client.test.ts`
**Test Prompt:**
```
"API client test dosyası oluştur. HTTP requests, 
error handling, interceptors test et."
```

**Error Handling:**
- **"API connection fails"** → `"Base URL ve CORS settings kontrol et"`
- **"Request interceptor issues"** → `"Token attachment ve header configuration kontrol et"`

---

## GÖREV 4.1: ANALYTICS & MONITORING 📊

### Ana Görev Listesi:
- [ ] **4.1.1** - Real-time analytics dashboard
- [ ] **4.1.2** - Performance metrics collection
- [ ] **4.1.3** - Report generation system
- [ ] **4.1.4** - WebSocket analytics streaming
- [ ] **4.1.5** - Data visualization components

### Alt Görev 4.1.1: Real-time Analytics Dashboard

**Etkilenen Dosyalar:**
- `analytics-implementation.md` (dashboard implementation)

**Implementation Prompt:**
```
"analytics-implementation.md'deki real-time dashboard'u implement et:
- Real-time metrics collection (Redis Streams)
- WebSocket-based live updates
- KPI cards (conversations, messages, response times)
- Interactive charts (Chart.js/Recharts)
- Time range filtering"
```

**Test Script:** `tests/test_analytics/test_dashboard.py`
**Test Prompt:**
```
"Analytics dashboard test dosyası oluştur. Metrics collection, 
real-time updates, chart rendering test et."
```

**Error Handling:**
- **"Real-time updates fail"** → `"WebSocket connection ve Redis pub/sub kontrol et"`
- **"Chart rendering issues"** → `"Data format ve chart library compatibility kontrol et"`

### Alt Görev 4.1.2: Performance Metrics Collection

**Implementation Prompt:**
```
"Performance metrics collection system'i implement et:
- Response time tracking
- Error rate monitoring  
- User satisfaction scoring
- Conversation completion rates
- System health metrics"
```

**Test Script:** `tests/test_analytics/test_metrics.py`
**Test Prompt:**
```
"Metrics collection test dosyası oluştur. Metric accuracy, 
aggregation, storage test et."
```

**Error Handling:**
- **"Metric calculation errors"** → `"Aggregation algorithms ve data types kontrol et"`
- **"High metrics storage load"** → `"Batch processing ve data retention policies implement et"`

### Alt Görev 4.1.3: Report Generation System

**Implementation Prompt:**
```
"Report generation system'i implement et:
- PDF report templates
- Scheduled report generation (Celery)
- Email delivery system
- Custom report builder
- Export formats (PDF, CSV, JSON)"
```

**Test Script:** `tests/test_analytics/test_reports.py`
**Test Prompt:**
```
"Report generation test dosyası oluştur. Template rendering, 
PDF generation, email delivery test et."
```

**Error Handling:**
- **"PDF generation fails"** → `"Template syntax ve data binding kontrol et"`
- **"Report delivery timeout"** → `"Email service configuration ve retry logic kontrol et"`

---

## GÖREV 5.1: TESTING & QUALITY ASSURANCE 🧪

### Ana Görev Listesi:
- [ ] **5.1.1** - Unit test implementation
- [ ] **5.1.2** - Integration testing setup
- [ ] **5.1.3** - End-to-end testing (Playwright)
- [ ] **5.1.4** - Performance testing
- [ ] **5.1.5** - Security testing

### Alt Görev 5.1.1: Unit Test Implementation

**Etkilenen Dosyalar:**
- `testing-strategy.md` (unit testing patterns)

**Implementation Prompt:**
```
"testing-strategy.md'deki unit test pattern'lerini kullanarak 
comprehensive test suite oluştur:
- Service layer tests (pytest fixtures)
- Repository tests (database mocking)
- API endpoint tests (FastAPI TestClient)
- Utility function tests
90%+ test coverage hedefle."
```

**Test Script:** Tüm `tests/` klasörü
**Test Prompt:**
```
"Unit test suite oluştur. Mock strategies, fixtures, 
assertion patterns implement et."
```

**Error Handling:**
- **"Test database connection fails"** → `"Test database isolation ve cleanup kontrol et"`
- **"Mock object issues"** → `"Mock configurations ve dependency injection kontrol et"`

### Alt Görev 5.1.2: Integration Testing Setup

**Implementation Prompt:**
```
"Integration testing setup:
- Database integration tests
- API workflow tests  
- Third-party service integration tests
- End-to-end business process tests
Test containers (Docker) kullan."
```

**Test Script:** `tests/integration/`
**Test Prompt:**
```
"Integration test suite oluştur. Service interactions, 
database transactions, external API calls test et."
```

**Error Handling:**
- **"Integration test flakiness"** → `"Test isolation ve cleanup strategies implement et"`
- **"External service dependency"** → `"Service mocking ve contract testing implement et"`

### Alt Görev 5.1.3: End-to-end Testing (Playwright)

**Implementation Prompt:**
```
"testing-strategy.md'deki E2E test senaryolarını Playwright ile implement et:
- User registration/login flows
- Chatbot creation workflows
- Training data upload processes
- Chat interactions
- Analytics dashboard navigation"
```

**Test Script:** `e2e-tests/`
**Test Prompt:**
```
"E2E test suite oluştur. Critical user journeys, 
cross-browser compatibility test et."
```

**Error Handling:**
- **"Browser automation fails"** → `"Playwright installation ve browser drivers kontrol et"`
- **"Test timing issues"** → `"Wait strategies ve element selectors optimize et"`

---

## GÖREV 6.1: DEPLOYMENT & PRODUCTION 🚀

### Ana Görev Listesi:
- [ ] **6.1.1** - Production infrastructure setup
- [ ] **6.1.2** - CI/CD pipeline configuration
- [ ] **6.1.3** - Monitoring ve logging setup
- [ ] **6.1.4** - Security hardening
- [ ] **6.1.5** - Performance optimization

### Alt Görev 6.1.1: Production Infrastructure Setup

**Implementation Prompt:**
```
"Production infrastructure setup:
- Docker containers (multi-stage build)
- Kubernetes/Docker Compose orchestration
- PostgreSQL database (RDS/managed)
- Redis cluster
- Load balancer configuration
- SSL/TLS certificates"
```

**Test Script:** `infrastructure/tests/`
**Test Prompt:**
```
"Infrastructure test dosyası oluştur. Container health, 
service connectivity, scaling test et."
```

**Error Handling:**
- **"Container startup fails"** → `"Dockerfile optimization ve health checks kontrol et"`
- **"Database connection issues"** → `"Connection pooling ve network configuration kontrol et"`

### Alt Görev 6.1.2: CI/CD Pipeline Configuration

**Implementation Prompt:**
```
"GitHub Actions CI/CD pipeline setup:
- Automated testing (unit, integration, E2E)
- Code quality checks (linting, type checking)
- Security scanning
- Multi-environment deployment
- Rollback mechanisms"
```

**Test Script:** `.github/workflows/`
**Test Prompt:**
```
"CI/CD pipeline test. Build processes, 
deployment stages, rollback scenarios test et."
```

**Error Handling:**
- **"Pipeline failure"** → `"Build steps ve dependency resolution kontrol et"`
- **"Deployment timeout"** → `"Deployment strategies ve health checks optimize et"`

---

Bu görev tabanlı PRD, her development adımını checkbox ile takip edilebilir hale getiriyor ve her görev için:

✅ **Etkilenen dosyalar** listesi
✅ **Implementation prompts** (ne yapılacağı)
✅ **Test script lokasyonları** ve prompts
✅ **Error handling prompts** (hata çözümleri)

Bu yapı ile development sürecini sistematik olarak takip edebilir ve her adımda test-driven approach uygulayabilirsiniz.