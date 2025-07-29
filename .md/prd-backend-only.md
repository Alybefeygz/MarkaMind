# MarkaMind Backend Development Roadmap (PRD)
**FastAPI + Supabase Backend Geliştirme Yol Haritası**

## 📋 Proje Genel Bakış

MarkaMind Backend, markalara özel yapay zeka destekli chatbot sisteminin API altyapısıdır. Bu PRD, sadece backend geliştirme sürecini kapsar ve her görevi checkbox sistemi ile takip edilebilir şekilde organize eder.

### 🎯 Backend Hedefleri
- **FastAPI** REST API altyapısı
- **Supabase** veritabanı ve authentication
- **RAG System** ile AI-powered chatbot responses
- **OpenRouter** AI model integration
- **Real-time analytics** ve monitoring
- **Scalable architecture** with background tasks

### 📊 Mevcut Dokümantasyon Durumu
✅ **README.md** - Proje genel bakış
✅ **endpoint.md** - 80+ API endpoint spesifikasyonu
✅ **fastapi-architecture.md** - Clean Architecture mimarisi
✅ **rag-system.md** - RAG implementasyon detayları
✅ **database-schema.md** - PostgreSQL schema ve optimizasyon
✅ **authentication-security.md** - JWT, RBAC, güvenlik
✅ **testing-strategy.md** - Test pyramid ve kalite güvencesi
✅ **analytics-implementation.md** - Real-time analytics sistemi
✅ **third-party-integrations.md** - OpenRouter, Supabase, Email, Storage

---

## 🗓️ BACKEND DEVELOPMENT ROADMAP

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
"FastAPI backend projesi için temel klasör yapısını oluştur. 
fastapi-architecture.md'deki yapıyı takip et. 
Backend-only struktur:

markamind-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # Environment settings
│   │   ├── database.py            # Supabase connection
│   │   └── logging.py             # Logging config
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py            # JWT, password hashing
│   │   ├── dependencies.py        # FastAPI dependencies
│   │   └── exceptions.py          # Custom exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # Base SQLAlchemy model  
│   │   ├── user.py                # User model
│   │   ├── chatbot.py             # Chatbot model
│   │   ├── conversation.py        # Conversation model
│   │   └── ...                    # Other models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                # Pydantic schemas
│   │   ├── chatbot.py             # Request/Response models
│   │   └── ...                    # Other schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # API dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # Main router
│   │       └── endpoints/
│   │           ├── auth.py        # Authentication endpoints
│   │           ├── chatbots.py    # Chatbot CRUD
│   │           ├── training.py    # Training data
│   │           ├── chat.py        # Chat endpoints
│   │           └── ...            # Other endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Authentication logic
│   │   ├── chatbot_service.py     # Chatbot business logic
│   │   ├── rag_service.py         # RAG system logic
│   │   ├── ai_service.py          # OpenRouter integration
│   │   └── ...                    # Other services
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                # Base repository pattern
│   │   ├── user_repository.py     # User data access
│   │   ├── chatbot_repository.py  # Chatbot data access
│   │   └── ...                    # Other repositories
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── supabase/
│   │   │   ├── __init__.py
│   │   │   └── client.py          # Supabase client
│   │   ├── openrouter/
│   │   │   ├── __init__.py
│   │   │   └── client.py          # OpenRouter client
│   │   └── ...                    # Other integrations
│   └── tasks/
│       ├── __init__.py
│       ├── celery_app.py          # Celery configuration
│       └── training_tasks.py      # Background tasks
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Test configuration
│   ├── test_api/                 # API endpoint tests
│   ├── test_services/            # Service layer tests
│   ├── test_models/              # Model tests
│   └── test_integrations/        # Integration tests
├── alembic/                      # Database migrations
├── requirements.txt              # Dependencies
├── requirements-dev.txt          # Dev dependencies
├── .env.example                  # Environment variables
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker compose
└── README.md                     # Project documentation"
```

**Test Script:** `tests/test_project_structure.py`
**Test Prompt:**
```
"Backend project structure test dosyası oluştur. 
Tüm gerekli klasörlerin ve __init__.py dosyalarının varlığını kontrol et.
Backend-specific folders'ı validate et."
```

**Error Handling:**
- **"Directory already exists"** → `"mkdir -p komutu ile güvenli klasör oluştur"`
- **"Permission denied"** → `"chmod/sudo ile yazma izni ver"`

### Alt Görev 1.1.2: Virtual Environment Kurulumu

**Etkilenen Dosyalar:**
- `fastapi-architecture.md` (environment setup)

**Implementation Prompt:**
```
"Python virtual environment oluştur ve aktif et:

# Backend çalışma dizini oluştur
mkdir markamind-backend && cd markamind-backend

# Virtual environment oluştur
python -m venv venv

# Aktif et (Windows)
venv\Scripts\activate

# Aktif et (Linux/Mac)  
source venv/bin/activate

# Python ve pip versiyonlarını kontrol et
python --version  # 3.9+ olmalı
pip --version

# Virtual environment'in aktif olduğunu doğrula
which python  # Linux/Mac
where python   # Windows"
```

**Test Script:** `tests/test_virtual_environment.py`
**Test Prompt:**
```
"Virtual environment test dosyası oluştur. 
Python version (3.9+), venv activation, pip functionality test et."
```

### Alt Görev 1.1.3: Dependencies Yükleme

**Etkilenen Dosyalar:**
- `third-party-integrations.md` (dependency listesi)
- `fastapi-architecture.md` (requirements.txt)

**Implementation Prompt:**
```
"Backend dependencies'i yükle. third-party-integrations.md'deki 
tüm backend dependency'leri requirements.txt'e ekle:

# requirements.txt
# FastAPI Core
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Database & ORM
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9

# Supabase
supabase==2.0.2

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Background Tasks
celery==5.3.4
redis==5.0.1

# HTTP Client
httpx==0.25.2

# Data Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Utilities
python-dotenv==1.0.0
aiofiles==23.2.1

# AI & RAG System
langchain==0.1.0
langchain-openai==0.0.2
chromadb==0.4.18
sentence-transformers==2.2.2
faiss-cpu==1.7.4
tiktoken==0.5.2
numpy==1.24.3
scipy==1.11.4

# File Processing
PyPDF2==3.0.1
pillow==10.1.0

# requirements-dev.txt  
# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Code Quality
black==23.12.1
isort==5.13.2
flake8==6.1.0
mypy==1.8.0

# Development
pre-commit==3.6.0

# Dependencies yükle
pip install -r requirements.txt
pip install -r requirements-dev.txt"
```

**Test Script:** `tests/test_dependencies.py`
**Test Prompt:**
```
"Backend dependencies test dosyası oluştur. 
Core packages (FastAPI, SQLAlchemy, Supabase), 
AI packages (langchain, chromadb), dev tools test et."
```

### Alt Görev 1.1.4: Core Configuration Dosyaları

**Etkilenen Dosyalar:**
- `authentication-security.md` (environment variables)
- `third-party-integrations.md` (API keys, Supabase settings)
- `fastapi-architecture.md` (settings.py yapısı)

**Implementation Prompt:**
```
"Backend core configuration dosyalarını oluştur:

1. .env.example:
# Database (Supabase)
DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenRouter AI
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=openai/gpt-3.5-turbo
OPENROUTER_EMBEDDING_MODEL=openai/text-embedding-ada-002

# Redis (for caching and Celery)
REDIS_URL=redis://localhost:6379

# Email
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

2. app/config/settings.py:
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "MarkaMind Backend API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Database (Supabase)
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenRouter AI
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_DEFAULT_MODEL: str = "openai/gpt-3.5-turbo"
    OPENROUTER_EMBEDDING_MODEL: str = "openai/text-embedding-ada-002"
    OPENROUTER_MAX_TOKENS: int = 2048
    OPENROUTER_TEMPERATURE: float = 0.7
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Email
    EMAIL_PROVIDER: str = "smtp"
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # File Storage
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: list = ["pdf", "txt", "docx", "md"]
    
    # RAG System
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    RAG_TOP_K: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

3. app/config/database.py:
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import settings

# Supabase PostgreSQL connection
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

4. app/config/logging.py:
import logging
import sys
from .settings import settings

def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("backend.log") if settings.ENVIRONMENT == "production" else logging.StreamHandler()
        ]
    )
    
    # Suppress third-party library logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)"
```

**Test Script:** `tests/test_configuration.py`
**Test Prompt:**
```
"Backend configuration test dosyası oluştur. 
Settings loading, Supabase connection, environment variables, 
logging setup test et."
```

### Alt Görev 1.1.5: Docker Containerization

**Etkilenen Dosyalar:**
- `fastapi-architecture.md` (Docker configuration)

**Implementation Prompt:**
```
"Backend Docker setup oluştur:

1. Dockerfile:
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

2. docker-compose.yml:
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/markamind
      - REDIS_URL=redis://redis:6379
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=markamind
      - POSTGRES_USER=postgres  
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/markamind
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - .:/app

volumes:
  postgres_data:
  redis_data:

3. .dockerignore:
__pycache__
*.pyc
*.pyo
*.pyd
.git
.pytest_cache
.coverage
.env
venv/
*.log
.DS_Store
.vscode/
.idea/"
```

**Test Script:** `tests/test_docker.py`
**Test Prompt:**
```
"Docker configuration test dosyası oluştur. 
Dockerfile build, docker-compose validation, 
service connectivity test et."
```

---

## GÖREV 1.2: SUPABASE INTEGRATION & AUTHENTICATION 🔐

### Ana Görev Listesi:
- [ ] **1.2.1** - Supabase client setup
- [ ] **1.2.2** - Database models (SQLAlchemy)
- [ ] **1.2.3** - Authentication system
- [ ] **1.2.4** - Row Level Security (RLS) setup
- [ ] **1.2.5** - Migration system (Alembic)

### Alt Görev 1.2.1: Supabase Client Setup

**Etkilenen Dosyalar:**
- `third-party-integrations.md` (Supabase configuration)

**Implementation Prompt:**
```
"third-party-integrations.md'deki Supabase client'ı 
app/integrations/supabase/client.py'da implement et:

from supabase import create_client, Client
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        # Main client for app operations
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        
        # Admin client for admin operations
        self.admin_client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    
    async def authenticate_user(self, email: str, password: str) -> dict:
        \"\"\"User authentication via Supabase Auth\"\"\"
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {"success": True, "user": response.user, "session": response.session}
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_user(self, email: str, password: str, metadata: dict = None) -> dict:
        \"\"\"Create new user with admin client\"\"\"
        try:
            response = self.admin_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": metadata or {}
            })
            return {"success": True, "user": response.user}
        except Exception as e:
            logger.error(f"User creation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def verify_jwt_token(self, token: str) -> dict:
        \"\"\"Verify JWT token\"\"\"
        try:
            response = self.client.auth.get_user(token)
            return {"valid": True, "user": response.user}
        except Exception as e:
            return {"valid": False, "error": str(e)}

# Global instance
supabase_client = SupabaseClient()"
```

**Test Script:** `tests/test_integrations/test_supabase.py`
**Test Prompt:**
```
"Supabase client test dosyası oluştur. 
Client initialization, auth methods, error handling test et."
```

### Alt Görev 1.2.2: Database Models (SQLAlchemy)

**Etkilenen Dosyalar:**
- `database-schema.md` (tablo yapıları)
- `fastapi-architecture.md` (model patterns)

**Implementation Prompt:**
```
"database-schema.md'deki tablo yapılarını SQLAlchemy models olarak implement et:

1. app/models/base.py:
from sqlalchemy import Column, Integer, DateTime, func, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

2. app/models/user.py:
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    company_name = Column(String(255))
    phone = Column(String(20))
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255))
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    chatbots = relationship("Chatbot", back_populates="user", cascade="all, delete-orphan")

3. app/models/chatbot.py:
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DECIMAL, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel

class Chatbot(BaseModel):
    __tablename__ = "chatbots"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50), default="general")
    language = Column(String(10), default="tr")
    status = Column(String(20), default="draft")  # draft, active, inactive, training
    
    # Settings and appearance as JSON
    settings = Column(JSONB, default={})
    appearance = Column(JSONB, default={})
    
    # Performance metrics
    message_count = Column(Integer, default=0)
    unique_users_count = Column(Integer, default=0)
    average_response_time = Column(DECIMAL(5,3), default=0.0)
    satisfaction_score = Column(DECIMAL(3,2), default=0.0)
    
    # Training info
    last_trained = Column(DateTime)
    training_data_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="chatbots")
    conversations = relationship("Conversation", back_populates="chatbot", cascade="all, delete-orphan")

Database schema'daki diğer tüm modelleri de benzer şekilde implement et."
```

**Test Script:** `tests/test_models/test_models.py`
**Test Prompt:**
```
"Database models test dosyası oluştur. 
Model creation, relationships, field validations, UUID generation test et."
```

### Alt Görev 1.2.3: Authentication System

**Etkilenen Dosyalar:**
- `authentication-security.md` (JWT implementation)

**Implementation Prompt:**
```
"authentication-security.md'deki authentication system'i implement et:

1. app/core/security.py:
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        return user_id
    except JWTError:
        return None

2. app/api/deps.py:
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.core.security import verify_token
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    token: str = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = verify_token(token.credentials)
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user"
```

**Test Script:** `tests/test_core/test_security.py`
**Test Prompt:**
```
"Authentication system test dosyası oluştur. 
JWT token creation/verification, password hashing, user authentication test et."
```

---

## GÖREV 1.3: API ENDPOINTS DEVELOPMENT 🌐

### Ana Görev Listesi:
- [ ] **1.3.1** - Authentication endpoints
- [ ] **1.3.2** - User management endpoints
- [ ] **1.3.3** - Chatbot CRUD endpoints
- [ ] **1.3.4** - Training data endpoints
- [ ] **1.3.5** - Chat endpoints

### Alt Görev 1.3.1: Authentication Endpoints

**Etkilenen Dosyalar:**
- `endpoint.md` (authentication endpoints)

**Implementation Prompt:**
```
"endpoint.md'deki authentication endpoint'lerini implement et:

app/api/v1/endpoints/auth.py:
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.auth import UserLogin, UserRegister, Token
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    \"\"\"User registration\"\"\"
    auth_service = AuthService(db)
    result = await auth_service.register_user(user_data)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result["token"]

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    \"\"\"User login\"\"\"
    auth_service = AuthService(db)
    result = await auth_service.authenticate_user(
        user_credentials.email,
        user_credentials.password
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    return result["token"]

@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    \"\"\"Refresh access token\"\"\"
    auth_service = AuthService()
    return await auth_service.create_token_for_user(current_user)

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    \"\"\"User logout\"\"\"
    # Token blacklisting could be implemented here
    return {"message": "Successfully logged out"}

Gerekli schemas'ları da oluştur:
app/schemas/auth.py"
```

**Test Script:** `tests/test_api/test_auth_endpoints.py`
**Test Prompt:**
```
"Authentication endpoints test dosyası oluştur. 
Registration, login, token refresh, logout flows test et."
```

### Alt Görev 1.3.2: User Management Endpoints

**Implementation Prompt:**
```
"endpoint.md'deki user management endpoint'lerini implement et:

app/api/v1/endpoints/users.py:
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.api.deps import get_current_user
from app.schemas.user import UserProfile, UserUpdate
from app.services.user_service import UserService

router = APIRouter()

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    \"\"\"Get current user profile\"\"\"
    return current_user

@router.put("/me", response_model=UserProfile)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Update current user profile\"\"\"
    user_service = UserService(db)
    return await user_service.update_user(current_user.id, user_update)

@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Delete current user account\"\"\"
    user_service = UserService(db)
    await user_service.delete_user(current_user.id)
    return {"message": "Account deleted successfully"}"
```

**Test Script:** `tests/test_api/test_user_endpoints.py`

### Alt Görev 1.3.3: Chatbot CRUD Endpoints

**Implementation Prompt:**
```
"endpoint.md'deki chatbot CRUD endpoint'lerini implement et:

app/api/v1/endpoints/chatbots.py:
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.api.deps import get_current_user
from app.schemas.chatbot import ChatbotCreate, ChatbotUpdate, ChatbotResponse
from app.services.chatbot_service import ChatbotService

router = APIRouter()

@router.get("/", response_model=List[ChatbotResponse])
async def list_chatbots(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"List user's chatbots\"\"\"
    chatbot_service = ChatbotService(db)
    return await chatbot_service.get_user_chatbots(current_user.id)

@router.post("/", response_model=ChatbotResponse)
async def create_chatbot(
    chatbot_data: ChatbotCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Create new chatbot\"\"\"
    chatbot_service = ChatbotService(db)
    return await chatbot_service.create_chatbot(current_user.id, chatbot_data)

@router.get("/{chatbot_id}", response_model=ChatbotResponse)
async def get_chatbot(
    chatbot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get specific chatbot\"\"\"
    chatbot_service = ChatbotService(db)
    chatbot = await chatbot_service.get_chatbot(chatbot_id)
    
    # Check ownership
    if chatbot.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return chatbot

@router.put("/{chatbot_id}", response_model=ChatbotResponse)
async def update_chatbot(
    chatbot_id: int,
    chatbot_update: ChatbotUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Update chatbot\"\"\"
    chatbot_service = ChatbotService(db)
    return await chatbot_service.update_chatbot(chatbot_id, chatbot_update, current_user.id)

@router.delete("/{chatbot_id}")
async def delete_chatbot(
    chatbot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Delete chatbot\"\"\"
    chatbot_service = ChatbotService(db)
    await chatbot_service.delete_chatbot(chatbot_id, current_user.id)
    return {"message": "Chatbot deleted successfully"}"
```

**Test Script:** `tests/test_api/test_chatbot_endpoints.py`

---

## GÖREV 2.1: RAG SYSTEM IMPLEMENTATION 🧠

### Ana Görev Listesi:
- [ ] **2.1.1** - OpenRouter integration
- [ ] **2.1.2** - Text processing pipeline
- [ ] **2.1.3** - ChromaDB vector database setup
- [ ] **2.1.4** - RAG service implementation
- [ ] **2.1.5** - Embedding generation system

### Alt Görev 2.1.1: OpenRouter Integration

**Etkilenen Dosyalar:**
- `third-party-integrations.md` (OpenRouter client)

**Implementation Prompt:**
```
"third-party-integrations.md'deki OpenRouter client'ı implement et:

app/integrations/openrouter/client.py:
import httpx
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://markamind.com",
            "X-Title": "MarkaMind AI Chatbot Platform"
        }
    
    async def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        **kwargs
    ) -> Dict[str, Any]:
        \"\"\"Create chat completion\"\"\"
        payload = {
            "model": model or settings.OPENROUTER_DEFAULT_MODEL,
            "messages": messages,
            "max_tokens": max_tokens or settings.OPENROUTER_MAX_TOKENS,
            "temperature": temperature or settings.OPENROUTER_TEMPERATURE,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"OpenRouter completion error: {e}")
            raise
    
    async def create_embedding(
        self,
        text: str,
        model: str = None
    ) -> List[float]:
        \"\"\"Create text embedding\"\"\"
        payload = {
            "model": model or settings.OPENROUTER_EMBEDDING_MODEL,
            "input": text
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"OpenRouter embedding error: {e}")
            raise

# Global instance
openrouter_client = OpenRouterClient()"
```

**Test Script:** `tests/test_integrations/test_openrouter.py`
**Test Prompt:**
```
"OpenRouter integration test dosyası oluştur. 
API calls, embedding generation, error handling test et."
```

### Alt Görev 2.1.2: Text Processing Pipeline

**Etkilenen Dosyalar:**
- `rag-system.md` (text processing)

**Implementation Prompt:**
```
"rag-system.md'deki text processing pipeline'ını implement et:

app/services/text_processor.py:
import PyPDF2
from typing import List, Dict
from io import BytesIO
import re
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        self.chunk_size = settings.RAG_CHUNK_SIZE
        self.chunk_overlap = settings.RAG_CHUNK_OVERLAP
    
    async def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        \"\"\"Extract text from PDF content\"\"\"
        try:
            pdf_stream = BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return self._clean_text(text)
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        \"\"\"Clean and normalize text\"\"\"
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep Turkish characters
        text = re.sub(r'[^\w\s\.,!?;:\-()âêîôûçğıöşüÂÊÎÔÛÇĞIÖŞÜ]', '', text)
        return text.strip()
    
    def create_chunks(self, text: str) -> List[Dict[str, Any]]:
        \"\"\"Split text into chunks with overlap\"\"\"
        chunks = []
        text_length = len(text)
        
        start = 0
        chunk_index = 0
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            # Try to break at sentence boundary
            if end < text_length:
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    "index": chunk_index,
                    "text": chunk_text,
                    "start_pos": start,
                    "end_pos": end,
                    "size": len(chunk_text)
                })
                chunk_index += 1
            
            start = max(start + 1, end - self.chunk_overlap)
        
        return chunks

# Global instance
text_processor = TextProcessor()"
```

**Test Script:** `tests/test_services/test_text_processor.py`

### Alt Görev 2.1.3: ChromaDB Vector Database Setup

**Etkilenen Dosyalar:**
- `rag-system.md` (ChromaDB configuration)

**Implementation Prompt:**
```
"rag-system.md'deki ChromaDB setup'ını implement et:

app/integrations/chromadb/client.py:
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

class ChromaDBClient:
    def __init__(self):
        # Create ChromaDB client with persistent storage
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))
    
    def get_or_create_collection(self, chatbot_id: int):
        \"\"\"Get or create collection for chatbot\"\"\"
        collection_name = f"chatbot_{chatbot_id}"
        
        try:
            collection = self.client.get_collection(name=collection_name)
        except ValueError:
            # Collection doesn't exist, create it
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        
        return collection
    
    async def add_embeddings(
        self,
        chatbot_id: int,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        \"\"\"Add embeddings to collection\"\"\"
        collection = self.get_or_create_collection(chatbot_id)
        
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    async def similarity_search(
        self,
        chatbot_id: int,
        query_embedding: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        \"\"\"Perform similarity search\"\"\"
        collection = self.get_or_create_collection(chatbot_id)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            similarity = 1 - results['distances'][0][i]  # Convert distance to similarity
            
            if similarity >= similarity_threshold:
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity": similarity
                })
        
        return formatted_results
    
    async def delete_collection(self, chatbot_id: int):
        \"\"\"Delete chatbot collection\"\"\"
        collection_name = f"chatbot_{chatbot_id}"
        try:
            self.client.delete_collection(name=collection_name)
        except ValueError:
            pass  # Collection doesn't exist

# Global instance
chromadb_client = ChromaDBClient()"
```

**Test Script:** `tests/test_integrations/test_chromadb.py`

### Alt Görev 2.1.4: RAG Service Implementation

**Etkilenen Dosyalar:**
- `rag-system.md` (RAG service)

**Implementation Prompt:**
```
"rag-system.md'deki RAGService'i implement et:

app/services/rag_service.py:
from typing import List, Dict, Any, Optional
from app.integrations.openrouter.client import openrouter_client
from app.integrations.chromadb.client import chromadb_client
from app.services.text_processor import text_processor
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.openrouter = openrouter_client
        self.chromadb = chromadb_client
        self.text_processor = text_processor
    
    async def process_training_data(
        self,
        chatbot_id: int,
        content: str,
        source_type: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        \"\"\"Process training data and create embeddings\"\"\"
        try:
            # 1. Create chunks
            chunks = self.text_processor.create_chunks(content)
            
            # 2. Generate embeddings for each chunk
            embeddings = []
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                # Generate embedding
                embedding = await self.openrouter.create_embedding(chunk["text"])
                
                embeddings.append(embedding)
                documents.append(chunk["text"])
                
                chunk_metadata = {
                    "source_type": source_type,
                    "chunk_index": chunk["index"],
                    "chunk_size": chunk["size"],
                    **(metadata or {})
                }
                metadatas.append(chunk_metadata)
                
                chunk_id = f"{chatbot_id}_{chunk['index']}"
                ids.append(chunk_id)
            
            # 3. Store in ChromaDB
            await self.chromadb.add_embeddings(
                chatbot_id=chatbot_id,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            return {
                "success": True,
                "chunks_processed": len(chunks),
                "embeddings_created": len(embeddings)
            }
            
        except Exception as e:
            logger.error(f"RAG processing error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_response(
        self,
        chatbot_id: int,
        user_query: str,
        chat_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        \"\"\"Generate RAG-enhanced response\"\"\"
        try:
            # 1. Create query embedding
            query_embedding = await self.openrouter.create_embedding(user_query)
            
            # 2. Similarity search
            relevant_chunks = await self.chromadb.similarity_search(
                chatbot_id=chatbot_id,
                query_embedding=query_embedding,
                top_k=settings.RAG_TOP_K,
                similarity_threshold=settings.RAG_SIMILARITY_THRESHOLD
            )
            
            # 3. Prepare context
            context = self._prepare_context(relevant_chunks)
            
            # 4. Create prompt
            messages = self._create_messages(user_query, context, chat_history)
            
            # 5. Generate response
            response = await self.openrouter.create_completion(messages=messages)
            
            return {
                "response": response["choices"][0]["message"]["content"],
                "sources": relevant_chunks,
                "context_used": context,
                "token_usage": response.get("usage", {})
            }
            
        except Exception as e:
            logger.error(f"RAG response generation error: {e}")
            raise
    
    def _prepare_context(self, chunks: List[Dict[str, Any]], max_length: int = 3000) -> str:
        \"\"\"Prepare context from retrieved chunks\"\"\"
        context_parts = []
        current_length = 0
        
        for chunk in chunks:
            text = chunk["document"]
            if current_length + len(text) > max_length:
                break
            
            context_parts.append(text)
            current_length += len(text)
        
        return "\n\n".join(context_parts)
    
    def _create_messages(
        self,
        user_query: str,
        context: str,
        chat_history: Optional[List[Dict]] = None
    ) -> List[Dict[str, str]]:
        \"\"\"Create message array for OpenRouter\"\"\"
        messages = []
        
        # System message with context
        system_message = f"\"\"\"Sen yardımcı bir AI asistanısın. Aşağıdaki bilgileri kullanarak kullanıcıya yardımcı ol:

{context}

Eğer verilen bilgilerde cevap yoksa, bunu belirt ve genel bilgilerle yardımcı olmaya çalış.\"\"\"
        
        messages.append({"role": "system", "content": system_message})
        
        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history[-5:])  # Last 5 messages
        
        # Current user query
        messages.append({"role": "user", "content": user_query})
        
        return messages

# Global instance
rag_service = RAGService()"
```

**Test Script:** `tests/test_services/test_rag_service.py`

---

## GÖREV 2.2: TRAINING DATA MANAGEMENT 📚

### Ana Görev Listesi:
- [ ] **2.2.1** - File upload endpoints
- [ ] **2.2.2** - Training data processing
- [ ] **2.2.3** - Background tasks (Celery)
- [ ] **2.2.4** - Progress tracking

### Alt Görev 2.2.1: File Upload Endpoints

**Etkilenen Dosyalar:**
- `endpoint.md` (training endpoints)

**Implementation Prompt:**
```
"endpoint.md'deki training endpoints'lerini implement et:

app/api/v1/endpoints/training.py:
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.api.deps import get_current_user
from app.services.training_service import TrainingService
from app.schemas.training import TrainingDataResponse

router = APIRouter()

@router.post("/upload/{chatbot_id}")
async def upload_training_file(
    chatbot_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Upload training file\"\"\"
    training_service = TrainingService(db)
    
    # Verify chatbot ownership
    await training_service.verify_chatbot_ownership(chatbot_id, current_user.id)
    
    # Process upload
    result = await training_service.process_file_upload(
        chatbot_id=chatbot_id,
        file=file,
        user_id=current_user.id
    )
    
    return result

@router.post("/text/{chatbot_id}")
async def upload_training_text(
    chatbot_id: int,
    text: str = Form(...),
    title: str = Form("Manual Text Input"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Upload training text directly\"\"\"
    training_service = TrainingService(db)
    
    # Verify chatbot ownership
    await training_service.verify_chatbot_ownership(chatbot_id, current_user.id)
    
    # Process text
    result = await training_service.process_text_input(
        chatbot_id=chatbot_id,
        text=text,
        title=title,
        user_id=current_user.id
    )
    
    return result

@router.get("/{chatbot_id}", response_model=List[TrainingDataResponse])
async def list_training_data(
    chatbot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"List training data for chatbot\"\"\"
    training_service = TrainingService(db)
    
    # Verify chatbot ownership
    await training_service.verify_chatbot_ownership(chatbot_id, current_user.id)
    
    return await training_service.get_training_data(chatbot_id)

@router.delete("/{data_id}")
async def delete_training_data(
    data_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Delete training data\"\"\"
    training_service = TrainingService(db)
    
    await training_service.delete_training_data(data_id, current_user.id)
    return {"message": "Training data deleted successfully"}

@router.post("/{chatbot_id}/retrain")
async def retrain_chatbot(
    chatbot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Trigger chatbot retraining\"\"\"
    training_service = TrainingService(db)
    
    # Verify chatbot ownership
    await training_service.verify_chatbot_ownership(chatbot_id, current_user.id)
    
    # Start background retraining task
    task_id = await training_service.start_retraining(chatbot_id)
    
    return {"message": "Retraining started", "task_id": task_id}"
```

**Test Script:** `tests/test_api/test_training_endpoints.py`

### Alt Görev 2.2.2: Training Data Processing

**Implementation Prompt:**
```
"Training data processing service'i implement et:

app/services/training_service.py:
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.models.training_data import TrainingData
from app.models.chatbot import Chatbot
from app.services.rag_service import rag_service
from app.services.text_processor import text_processor
from app.tasks.training_tasks import process_training_file_task
import uuid
import aiofiles
import os

class TrainingService:
    def __init__(self, db: Session):
        self.db = db
    
    async def verify_chatbot_ownership(self, chatbot_id: int, user_id: int):
        \"\"\"Verify user owns the chatbot\"\"\"
        chatbot = self.db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
        if not chatbot:
            raise HTTPException(status_code=404, detail="Chatbot not found")
        
        if chatbot.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        return chatbot
    
    async def process_file_upload(
        self,
        chatbot_id: int,
        file: UploadFile,
        user_id: int
    ) -> dict:
        \"\"\"Process uploaded file\"\"\"
        # Validate file
        await self._validate_file(file)
        
        # Save file temporarily
        file_path = await self._save_upload_file(file)
        
        # Create training data record
        training_data = TrainingData(
            chatbot_id=chatbot_id,
            type=self._get_file_type(file.filename),
            filename=file.filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file.size,
            status="pending"
        )
        
        self.db.add(training_data)
        self.db.commit()
        self.db.refresh(training_data)
        
        # Queue background processing
        task = process_training_file_task.delay(
            training_data_id=training_data.id,
            chatbot_id=chatbot_id,
            file_path=file_path
        )
        
        return {
            "training_data_id": training_data.id,
            "task_id": task.id,
            "status": "processing",
            "message": "File uploaded and queued for processing"
        }
    
    async def process_text_input(
        self,
        chatbot_id: int,
        text: str,
        title: str,
        user_id: int
    ) -> dict:
        \"\"\"Process text input directly\"\"\"
        # Create training data record
        training_data = TrainingData(
            chatbot_id=chatbot_id,
            type="manual",
            filename=title,
            original_filename=title,
            content_preview=text[:500],
            status="processing"
        )
        
        self.db.add(training_data)
        self.db.commit()
        self.db.refresh(training_data)
        
        # Process immediately with RAG service
        try:
            result = await rag_service.process_training_data(
                chatbot_id=chatbot_id,
                content=text,
                source_type="manual",
                metadata={"title": title}
            )
            
            if result["success"]:
                training_data.status = "processed"
                training_data.chunk_count = result["chunks_processed"]
            else:
                training_data.status = "failed"
                training_data.processing_log = result["error"]
            
            self.db.commit()
            
            return {
                "training_data_id": training_data.id,
                "status": training_data.status,
                "chunks_processed": result.get("chunks_processed", 0)
            }
            
        except Exception as e:
            training_data.status = "failed"
            training_data.processing_log = str(e)
            self.db.commit()
            raise
    
    async def _validate_file(self, file: UploadFile):
        \"\"\"Validate uploaded file\"\"\"
        # Check file size
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Check file type
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )
    
    async def _save_upload_file(self, file: UploadFile) -> str:
        \"\"\"Save uploaded file to disk\"\"\"
        # Create uploads directory if not exists
        os.makedirs("uploads", exist_ok=True)
        
        # Generate unique filename
        file_ext = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = f"uploads/{unique_filename}"
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path
    
    def _get_file_type(self, filename: str) -> str:
        \"\"\"Get file type from extension\"\"\"
        return filename.split('.')[-1].lower()"
```

**Test Script:** `tests/test_services/test_training_service.py`

### Alt Görev 2.2.3: Background Tasks (Celery)

**Implementation Prompt:**
```
"Celery background tasks setup:

1. app/tasks/celery_app.py:
from celery import Celery
from app.config.settings import settings

celery_app = Celery(
    "markamind",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.training_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

2. app/tasks/training_tasks.py:
from celery import current_task
from app.tasks.celery_app import celery_app
from app.services.rag_service import rag_service
from app.services.text_processor import text_processor
from app.models.training_data import TrainingData
from app.config.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_training_file_task(self, training_data_id: int, chatbot_id: int, file_path: str):
    \"\"\"Background task to process training file\"\"\"
    db = SessionLocal()
    
    try:
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Reading file...'}
        )
        
        # Get training data record
        training_data = db.query(TrainingData).filter(TrainingData.id == training_data_id).first()
        if not training_data:
            raise Exception("Training data not found")
        
        # Read file content
        if training_data.type == "pdf":
            with open(file_path, 'rb') as f:
                pdf_content = f.read()
            content = await text_processor.extract_text_from_pdf(pdf_content)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'Processing content...'}
        )
        
        # Process with RAG service
        result = await rag_service.process_training_data(
            chatbot_id=chatbot_id,
            content=content,
            source_type=training_data.type,
            metadata={"filename": training_data.filename}
        )
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Finalizing...'}
        )
        
        # Update training data record
        if result["success"]:
            training_data.status = "processed"
            training_data.chunk_count = result["chunks_processed"]
            training_data.content_preview = content[:500]
        else:
            training_data.status = "failed"
            training_data.processing_log = result["error"]
        
        db.commit()
        
        return {
            "training_data_id": training_data_id,
            "status": training_data.status,
            "chunks_processed": result.get("chunks_processed", 0)
        }
        
    except Exception as e:
        logger.error(f"Training task error: {e}")
        
        # Update training data as failed
        training_data = db.query(TrainingData).filter(TrainingData.id == training_data_id).first()
        if training_data:
            training_data.status = "failed"
            training_data.processing_log = str(e)
            db.commit()
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
    
    finally:
        db.close()
        
        # Clean up temporary file
        try:
            os.remove(file_path)
        except:
            pass"
```

**Test Script:** `tests/test_tasks/test_training_tasks.py`

---

## GÖREV 3.1: CHAT SYSTEM & API COMPLETION 💬

### Ana Görev Listesi:
- [ ] **3.1.1** - Chat endpoints implementation
- [ ] **3.1.2** - WebSocket real-time messaging
- [ ] **3.1.3** - Conversation management
- [ ] **3.1.4** - Analytics endpoints
- [ ] **3.1.5** - Admin endpoints

### Alt Görev 3.1.1: Chat Endpoints Implementation

**Etkilenen Dosyalar:**
- `endpoint.md` (chat endpoints)

**Implementation Prompt:**
```
"endpoint.md'deki chat endpoints'lerini implement et:

app/api/v1/endpoints/chat.py:
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.api.deps import get_current_user
from app.services.chat_service import ChatService
from app.schemas.chat import ChatMessage, ConversationResponse

router = APIRouter()

@router.post("/{chatbot_id}/conversation")
async def start_conversation(
    chatbot_id: int,
    session_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Start new conversation\"\"\"
    chat_service = ChatService(db)
    return await chat_service.start_conversation(chatbot_id, current_user.id, session_id)

@router.post("/{chatbot_id}/message")
async def send_message(
    chatbot_id: int,
    message_data: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Send message to chatbot\"\"\"
    chat_service = ChatService(db)
    return await chat_service.process_message(chatbot_id, message_data, current_user.id)

@router.get("/{chatbot_id}/conversations")
async def get_conversations(
    chatbot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get chatbot conversations\"\"\"
    chat_service = ChatService(db)
    return await chat_service.get_conversations(chatbot_id, current_user.id)

@router.get("/conversation/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get conversation messages\"\"\"
    chat_service = ChatService(db)
    return await chat_service.get_conversation_messages(conversation_id, current_user.id)

@router.websocket("/{chatbot_id}/ws")
async def websocket_chat(
    websocket: WebSocket,
    chatbot_id: int,
    db: Session = Depends(get_db)
):
    \"\"\"WebSocket chat endpoint\"\"\"
    chat_service = ChatService(db)
    await chat_service.handle_websocket_connection(websocket, chatbot_id)"
```

**Test Script:** `tests/test_api/test_chat_endpoints.py`

### Alt Görev 3.1.2: WebSocket Real-time Messaging

**Implementation Prompt:**
```
"WebSocket real-time messaging implement et:

app/services/websocket_manager.py:
from fastapi import WebSocket
from typing import Dict, List, Set
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        # Active connections per chatbot
        self.connections: Dict[int, Set[WebSocket]] = {}
        # Connection to user mapping
        self.user_connections: Dict[WebSocket, int] = {}
    
    async def connect(self, websocket: WebSocket, chatbot_id: int, user_id: int = None):
        \"\"\"Accept WebSocket connection\"\"\"
        await websocket.accept()
        
        if chatbot_id not in self.connections:
            self.connections[chatbot_id] = set()
        
        self.connections[chatbot_id].add(websocket)
        
        if user_id:
            self.user_connections[websocket] = user_id
        
        logger.info(f"WebSocket connected for chatbot {chatbot_id}")
    
    def disconnect(self, websocket: WebSocket, chatbot_id: int):
        \"\"\"Remove WebSocket connection\"\"\"
        if chatbot_id in self.connections:
            self.connections[chatbot_id].discard(websocket)
        
        if websocket in self.user_connections:
            del self.user_connections[websocket]
        
        logger.info(f"WebSocket disconnected for chatbot {chatbot_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        \"\"\"Send message to specific WebSocket\"\"\"
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_chatbot(self, chatbot_id: int, message: dict):
        \"\"\"Broadcast message to all connections for a chatbot\"\"\"
        if chatbot_id not in self.connections:
            return
        
        disconnected = set()
        
        for websocket in self.connections[chatbot_id]:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected WebSockets
        for websocket in disconnected:
            self.connections[chatbot_id].discard(websocket)

# Global instance
websocket_manager = WebSocketManager()"
```

**Test Script:** `tests/test_services/test_websocket_manager.py`

---

## GÖREV 4.1: TESTING & QUALITY ASSURANCE 🧪

### Ana Görev Listesi:
- [ ] **4.1.1** - Unit test implementation
- [ ] **4.1.2** - Integration tests
- [ ] **4.1.3** - API endpoint tests
- [ ] **4.1.4** - Performance tests
- [ ] **4.1.5** - Test coverage setup

### Alt Görev 4.1.1: Unit Test Implementation

**Etkilenen Dosyalar:**
- `testing-strategy.md` (unit testing patterns)

**Implementation Prompt:**
```
"testing-strategy.md'deki unit test patterns'ı kullanarak comprehensive test suite oluştur:

1. tests/conftest.py:
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.config.database import get_db, Base
from app.models import *

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        first_name="Test",
        last_name="User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, test_user):
    login_data = {"email": "test@example.com", "password": "testpassword"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

2. tests/test_services/test_rag_service.py:
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.rag_service import RAGService

@pytest.fixture
def rag_service():
    return RAGService()

@pytest.mark.asyncio
async def test_process_training_data_success(rag_service):
    \"\"\"Test successful training data processing\"\"\"
    # Mock dependencies
    with patch.object(rag_service.openrouter, 'create_embedding') as mock_embedding, \
         patch.object(rag_service.chromadb, 'add_embeddings') as mock_add:
        
        mock_embedding.return_value = [0.1, 0.2, 0.3]  # Mock embedding
        mock_add.return_value = None
        
        result = await rag_service.process_training_data(
            chatbot_id=1,
            content="Test content for processing",
            source_type="manual"
        )
        
        assert result["success"] is True
        assert result["chunks_processed"] > 0
        assert result["embeddings_created"] > 0

@pytest.mark.asyncio
async def test_generate_response_with_context(rag_service):
    \"\"\"Test response generation with RAG context\"\"\"
    with patch.object(rag_service.openrouter, 'create_embedding') as mock_embed, \
         patch.object(rag_service.chromadb, 'similarity_search') as mock_search, \
         patch.object(rag_service.openrouter, 'create_completion') as mock_completion:
        
        # Mock responses
        mock_embed.return_value = [0.1, 0.2, 0.3]
        mock_search.return_value = [
            {"document": "Relevant context", "similarity": 0.8}
        ]
        mock_completion.return_value = {
            "choices": [{"message": {"content": "AI response"}}],
            "usage": {"total_tokens": 100}
        }
        
        result = await rag_service.generate_response(
            chatbot_id=1,
            user_query="Test query"
        )
        
        assert "response" in result
        assert "sources" in result
        assert result["response"] == "AI response"

3. tests/test_api/test_auth_endpoints.py:
import pytest
from fastapi.testclient import TestClient

def test_register_user(client):
    \"\"\"Test user registration\"\"\"
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "first_name": "New",
        "last_name": "User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_success(client, test_user):
    \"\"\"Test successful login\"\"\"
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_invalid_credentials(client):
    \"\"\"Test login with invalid credentials\"\"\"
    login_data = {
        "email": "wrong@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 401

def test_protected_endpoint(client, auth_headers):
    \"\"\"Test accessing protected endpoint\"\"\"
    response = client.get("/api/v1/users/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com""
```

**Test Script:** Yukarıdaki test dosyaları
**Test Prompt:**
```
"90%+ test coverage hedefleyerek comprehensive test suite oluştur. 
Mock strategies, fixtures, async testing patterns kullan."
```

---

## GÖREV 5.1: DEPLOYMENT & PRODUCTION 🚀

### Ana Görev Listesi:
- [ ] **5.1.1** - Production configuration
- [ ] **5.1.2** - Docker production setup
- [ ] **5.1.3** - Database migration strategy
- [ ] **5.1.4** - Monitoring ve logging
- [ ] **5.1.5** - Security hardening

### Alt Görev 5.1.1: Production Configuration

**Implementation Prompt:**
```
"Production configuration setup:

1. .env.production:
# Production Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database (Supabase Production)
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
SUPABASE_URL=https://[project].supabase.co
SUPABASE_KEY=[production-anon-key]
SUPABASE_SERVICE_KEY=[production-service-key]

# Security (Strong production keys)
SECRET_KEY=[generate-strong-secret-key]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenRouter (Production limits)
OPENROUTER_API_KEY=[production-api-key]
OPENROUTER_DEFAULT_MODEL=openai/gpt-3.5-turbo
OPENROUTER_MAX_TOKENS=2048

# Redis (Production instance)
REDIS_URL=redis://[production-redis-host]:6379

# Email (Production SMTP)
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=[production-email]
SMTP_PASSWORD=[app-password]

2. app/config/production.py:
from .settings import Settings

class ProductionSettings(Settings):
    # Production-specific overrides
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Enhanced security
    COOKIE_SECURE: bool = True
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "strict"
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # 1 hour
    
    # CORS (restrict in production)
    ALLOWED_ORIGINS: list = ["https://yourdomain.com"]
    
    # Database connection pooling
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_TIMEOUT: int = 30"
```

**Test Script:** `tests/test_production_config.py`

---

Bu backend-only PRD ile hayata geçireceğiniz:

## ✅ **Kapsamlı Backend Sistemi**

### 🔧 **FastAPI Backend Infrastructure**
- Authentication & JWT security
- 80+ API endpoints  
- Clean Architecture pattern
- Dependency injection
- Error handling middleware

### 🗄️ **Supabase Integration**
- PostgreSQL database
- Row Level Security (RLS)
- Real-time subscriptions
- File storage
- Authentication

### 🧠 **RAG AI System**
- OpenRouter model integration
- ChromaDB vector database
- Text processing pipeline
- Semantic search
- Context-aware responses

### 📊 **Analytics & Monitoring**
- Real-time metrics collection
- WebSocket live updates
- Performance tracking
- Background task monitoring

### 🧪 **Testing & Quality**
- 90%+ test coverage
- Unit & integration tests
- API endpoint testing
- Performance testing

### 🚀 **Production Ready**
- Docker containerization
- Production configuration
- Security hardening
- Deployment automation

Bu PRD ile **sadece backend** geliştirerek tam fonksiyonel bir chatbot API sistemi oluşturacaksınız! 🎯