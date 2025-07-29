# MarkaMind FastAPI Mimarisi

## Genel Mimari Yaklaşımı

MarkaMind projesi, **Clean Architecture** ve **Domain-Driven Design (DDD)** prensiplerine dayalı, modüler ve ölçeklenebilir bir FastAPI mimarisi kullanacak.

## 1. Proje Dizin Yapısı

```
markamind-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI uygulama giriş noktası
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py             # Uygulama ayarları
│   │   ├── database.py             # Veritabanı konfigürasyonu
│   │   └── logging.py              # Log konfigürasyonu
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py             # JWT, password hashing
│   │   ├── dependencies.py         # Ortak dependency'ler
│   │   ├── exceptions.py           # Custom exception'lar
│   │   ├── middleware.py           # Custom middleware'ler
│   │   └── utils.py                # Yardımcı fonksiyonlar
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base model sınıfı
│   │   ├── user.py                 # User model
│   │   ├── chatbot.py              # Chatbot model
│   │   ├── conversation.py         # Conversation model
│   │   ├── training_data.py        # Training data model
│   │   ├── rag_embedding.py        # RAG embedding model
│   │   ├── rag_chunk.py            # RAG chunk model
│   │   ├── subscription.py         # Subscription model
│   │   ├── virtual_store.py        # Virtual store model
│   │   ├── analytics.py            # Analytics model
│   │   ├── webhook.py              # Webhook model
│   │   └── file.py                 # File model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base Pydantic schemas
│   │   ├── user.py                 # User schemas
│   │   ├── auth.py                 # Authentication schemas
│   │   ├── chatbot.py              # Chatbot schemas
│   │   ├── conversation.py         # Conversation schemas
│   │   ├── training.py             # Training schemas
│   │   ├── rag.py                  # RAG system schemas
│   │   ├── subscription.py         # Subscription schemas
│   │   ├── virtual_store.py        # Virtual store schemas
│   │   ├── analytics.py            # Analytics schemas
│   │   ├── webhook.py              # Webhook schemas
│   │   └── file.py                 # File schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                 # API dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py           # Main API router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py         # Authentication endpoints
│   │           ├── users.py        # User management endpoints
│   │           ├── chatbots.py     # Chatbot endpoints
│   │           ├── training.py     # Training endpoints
│   │           ├── rag.py          # RAG system endpoints
│   │           ├── chat.py         # Chat endpoints
│   │           ├── analytics.py    # Analytics endpoints
│   │           ├── subscriptions.py # Subscription endpoints
│   │           ├── virtual_store.py # Virtual store endpoints
│   │           ├── webhooks.py     # Webhook endpoints
│   │           ├── files.py        # File management endpoints
│   │           └── admin.py        # Admin endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py         # Authentication logic
│   │   ├── chatbot_service.py      # Chatbot business logic
│   │   ├── training_service.py     # Training logic
│   │   ├── rag_service.py          # RAG system logic
│   │   ├── ai_service.py           # AI model integration
│   │   ├── analytics_service.py    # Analytics logic
│   │   ├── subscription_service.py # Subscription logic
│   │   ├── virtual_store_service.py # Virtual store logic
│   │   ├── webhook_service.py      # Webhook logic
│   │   ├── file_service.py         # File handling logic
│   │   ├── email_service.py        # Email sending logic
│   │   └── notification_service.py # Notification logic
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base repository pattern
│   │   ├── user_repository.py      # User data access
│   │   ├── chatbot_repository.py   # Chatbot data access
│   │   ├── conversation_repository.py # Conversation data access
│   │   ├── training_repository.py  # Training data access
│   │   ├── rag_repository.py       # RAG data access
│   │   ├── subscription_repository.py # Subscription data access
│   │   ├── analytics_repository.py # Analytics data access
│   │   ├── webhook_repository.py   # Webhook data access
│   │   └── file_repository.py      # File data access
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py          # Celery configuration
│   │   ├── training_tasks.py       # Training background tasks
│   │   ├── rag_tasks.py            # RAG processing background tasks
│   │   ├── analytics_tasks.py      # Analytics background tasks
│   │   └── notification_tasks.py   # Notification background tasks
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py            # Test configuration
│       ├── test_auth.py           # Authentication tests
│       ├── test_chatbots.py       # Chatbot tests
│       ├── test_training.py       # Training tests
│       ├── test_rag.py            # RAG system tests
│       └── test_analytics.py      # Analytics tests
├── alembic/                       # Database migrations
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── scripts/
│   ├── start-dev.sh              # Development startup script
│   ├── start-prod.sh             # Production startup script
│   └── create-superuser.py       # Admin user creation
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── .env.example                  # Environment variables example
├── docker-compose.yml            # Docker configuration
├── Dockerfile                    # Docker image definition
└── README.md                     # Project documentation
```

## 2. Katman Mimarisi

### 2.1 Presentation Layer (API Endpoints)
- FastAPI router'ları
- Request/Response validation (Pydantic)
- HTTP status code yönetimi
- API documentation (OpenAPI/Swagger)

### 2.2 Business Logic Layer (Services)
- Domain business rules
- Use case implementations
- External service integrations
- Data validation ve transformation

### 2.3 Data Access Layer (Repositories)
- Database operations
- Query optimization
- Data mapping
- Transaction management

### 2.4 Infrastructure Layer
- Database configuration
- External API clients
- File storage
- Caching
- Logging

## 3. Temel Teknolojiler ve Kütüphaneler

```python
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
httpx==0.25.2
aiofiles==23.2.1
pillow==10.1.0
PyPDF2==3.0.1
openai==1.3.7
supabase==2.0.2

# RAG System Dependencies
langchain==0.1.0
langchain-openai==0.0.2
chromadb==0.4.18
sentence-transformers==2.2.2
faiss-cpu==1.7.4
tiktoken==0.5.2
numpy==1.24.3
scipy==1.11.4

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

## 4. Ana Konfigürasyon Dosyaları

### 4.1 app/config/settings.py
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # AI Service
    OPENAI_API_KEY: str
    
    # RAG System
    RAG_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    RAG_TOP_K: int = 5
    
    # Vector Database
    CHROMA_DB_PATH: str = "chroma_db"
    FAISS_INDEX_PATH: str = "faiss_indexes"
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 4.2 app/main.py
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.core.exceptions import CustomException
from app.core.middleware import LoggingMiddleware
from app.api.v1.router import api_router

app = FastAPI(
    title="MarkaMind API",
    description="AI-powered chatbot platform API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

# Exception handlers
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.error_code, "message": exc.message}
    )

# Include routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

## 5. Database Layer

### 5.1 SQLAlchemy Models (app/models/base.py)
```python
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr

Base = declarative_base()

class BaseModel:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 5.2 Repository Pattern (app/repositories/base.py)
```python
from typing import Generic, Type, TypeVar, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    async def get(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: int) -> ModelType:
        obj = self.db.query(self.model).get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj
```

## 6. Service Layer Architecture

### 6.1 Base Service Pattern
```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from app.repositories.base import BaseRepository

ServiceType = TypeVar("ServiceType")

class BaseService(ABC, Generic[ServiceType]):
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    @abstractmethod
    async def create(self, **kwargs):
        pass
    
    @abstractmethod
    async def get_by_id(self, id: int):
        pass
    
    @abstractmethod
    async def update(self, id: int, **kwargs):
        pass
    
    @abstractmethod
    async def delete(self, id: int):
        pass
```

### 6.2 Chatbot Service Example
```python
from app.services.base import BaseService
from app.repositories.chatbot_repository import ChatbotRepository
from app.schemas.chatbot import ChatbotCreate, ChatbotUpdate

class ChatbotService(BaseService):
    def __init__(self, repository: ChatbotRepository):
        super().__init__(repository)
    
    async def create_chatbot(self, user_id: int, chatbot_data: ChatbotCreate):
        # Business logic
        chatbot_dict = chatbot_data.dict()
        chatbot_dict["user_id"] = user_id
        chatbot_dict["status"] = "draft"
        
        return await self.repository.create(chatbot_dict)
    
    async def train_chatbot(self, chatbot_id: int, training_data):
        # Training business logic
        # Queue background task for training
        pass
```

## 7. Background Tasks (Celery)

### 7.1 Celery Configuration
```python
# app/tasks/celery_app.py
from celery import Celery
from app.config.settings import settings

celery_app = Celery(
    "markamind",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.training_tasks", "app.tasks.analytics_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# RAG Tasks Configuration
celery_app.conf.task_routes = {
    'app.tasks.rag_tasks.*': {'queue': 'rag'},
    'app.tasks.training_tasks.*': {'queue': 'training'},
}
```

### 7.2 Training Tasks
```python
# app/tasks/training_tasks.py
from app.tasks.celery_app import celery_app
from app.services.training_service import TrainingService

@celery_app.task
def process_pdf_training(chatbot_id: int, file_path: str):
    training_service = TrainingService()
    return training_service.process_pdf(chatbot_id, file_path)

@celery_app.task
def retrain_chatbot(chatbot_id: int):
    training_service = TrainingService()
    return training_service.retrain(chatbot_id)
```

### 7.3 RAG Tasks
```python
# app/tasks/rag_tasks.py
from app.tasks.celery_app import celery_app
from app.services.rag_service import RAGService

@celery_app.task(bind=True)
def create_embeddings(self, chatbot_id: int, data_ids: list):
    """Create embeddings for training data chunks"""
    rag_service = RAGService()
    try:
        result = rag_service.create_embeddings(chatbot_id, data_ids)
        return result
    except Exception as exc:
        self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task(bind=True)
def optimize_vector_database(self, chatbot_id: int):
    """Optimize vector database by removing duplicates and rebuilding index"""
    rag_service = RAGService()
    try:
        result = rag_service.optimize_database(chatbot_id)
        return result
    except Exception as exc:
        self.retry(exc=exc, countdown=120, max_retries=2)

@celery_app.task
def batch_similarity_search(chatbot_id: int, queries: list):
    """Perform batch similarity search for multiple queries"""
    rag_service = RAGService()
    return rag_service.batch_search(chatbot_id, queries)
```

## 8. Authentication & Authorization

### 8.1 JWT Implementation
```python
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### 8.2 Dependencies
```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from app.config.settings import settings
from app.models.user import User

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> User:
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user from database
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
```

## 9. Error Handling

### 9.1 Custom Exceptions
```python
# app/core/exceptions.py
class CustomException(Exception):
    def __init__(self, message: str, status_code: int = 400, error_code: str = "GENERIC_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

class ChatbotNotFoundError(CustomException):
    def __init__(self):
        super().__init__(
            message="Chatbot not found",
            status_code=404,
            error_code="CHATBOT_NOT_FOUND"
        )

class InsufficientPermissionsError(CustomException):
    def __init__(self):
        super().__init__(
            message="Insufficient permissions",
            status_code=403,
            error_code="INSUFFICIENT_PERMISSIONS"
        )
```

## 10. Testing Strategy

### 10.1 Test Configuration
```python
# app/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.config.database import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    # Create test user and return auth headers
    pass
```

## 11. Deployment Architecture

### 11.1 Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.2 Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/markamind
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=markamind
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

## 12. Monitoring & Logging

### 12.1 Logging Configuration
```python
# app/config/logging.py
import logging
import sys
from app.config.settings import settings

def setup_logging():
    logging.basicConfig(
        level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )
```

### 12.2 Middleware for Request Logging
```python
# app/core/middleware.py
import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

class LoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            start_time = time.time()
            
            response = await self.app(scope, receive, send)
            
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url} - {process_time:.3f}s"
            )
            
            return response
        
        return await self.app(scope, receive, send)
```

## 13. Güvenlik Önlemleri

### 13.1 Rate Limiting
```python
# app/core/rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Usage in endpoints
@app.post("/api/v1/chat/message")
@limiter.limit("10/minute")
async def send_message(request: Request, ...):
    pass
```

### 13.2 Input Validation
```python
# app/schemas/base.py
from pydantic import BaseModel, validator
from typing import Optional

class BaseSchema(BaseModel):
    class Config:
        str_strip_whitespace = True
        validate_assignment = True
        use_enum_values = True

class ChatbotCreate(BaseSchema):
    name: str
    description: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError('Name must be at least 3 characters')
        return v
```

Bu mimari, MarkaMind projesinin tüm gereksinimlerini karşılayacak, ölçeklenebilir ve maintainable bir FastAPI uygulaması sağlar.