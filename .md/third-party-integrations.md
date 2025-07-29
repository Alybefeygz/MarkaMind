# MarkaMind Third-Party Integrations - Üçüncü Taraf Entegrasyonları

## 1. Genel Bakış

MarkaMind platformu, güçlü ve ölçeklenebilir bir çözüm sağlamak için çeşitli üçüncü taraf servisleri entegre eder. Bu dokümantasyon, tüm external service entegrasyonlarının konfigürasyonu, kullanımı ve best practice'lerini detaylandırır.

### 1.1 Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MarkaMind Platform                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ OpenRouter  │    │  Supabase   │    │    Email    │         │
│  │   AI API    │    │  Database   │    │   Service   │         │
│  │             │    │   Auth      │    │  (SMTP)     │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                   │              │
│         ▼                   ▼                   ▼              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              FastAPI Application                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                   │                   │              │
│         ▼                   ▼                   ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  File       │    │   Redis     │    │  Background │         │
│  │ Storage     │    │   Cache     │    │   Tasks     │         │
│  │ (Supabase)  │    │  Session    │    │  (Celery)   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## 2. OpenRouter API Entegrasyonu

OpenRouter, multiple AI model'lere unified API access sağlayan bir servisdir. MarkaMind'da chatbot responses ve RAG embeddings için kullanılır.

### 2.1 OpenRouter Configuration

#### Environment Variables
```bash
# .env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=openai/gpt-3.5-turbo
OPENROUTER_EMBEDDING_MODEL=openai/text-embedding-ada-002
OPENROUTER_MAX_TOKENS=2048
OPENROUTER_TEMPERATURE=0.7
OPENROUTER_TIMEOUT=30
```

#### Settings Configuration
```python
# app/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenRouter Configuration
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_DEFAULT_MODEL: str = "openai/gpt-3.5-turbo"
    OPENROUTER_EMBEDDING_MODEL: str = "openai/text-embedding-ada-002"
    OPENROUTER_MAX_TOKENS: int = 2048
    OPENROUTER_TEMPERATURE: float = 0.7
    OPENROUTER_TIMEOUT: int = 30
    
    # Model specific configurations
    OPENROUTER_MODELS: dict = {
        "gpt-3.5-turbo": {
            "name": "openai/gpt-3.5-turbo",
            "max_tokens": 4096,
            "cost_per_token": 0.0000015,
            "supports_system_messages": True
        },
        "gpt-4": {
            "name": "openai/gpt-4",
            "max_tokens": 8192,
            "cost_per_token": 0.00003,
            "supports_system_messages": True
        },
        "claude-3": {
            "name": "anthropic/claude-3-sonnet",
            "max_tokens": 4096,
            "cost_per_token": 0.000015,
            "supports_system_messages": True
        },
        "llama-2": {
            "name": "meta-llama/llama-2-70b-chat",
            "max_tokens": 4096,
            "cost_per_token": 0.0000007,
            "supports_system_messages": False
        }
    }

settings = Settings()
```

### 2.2 OpenRouter Client Implementation

#### Base Client
```python
# app/integrations/openrouter/client.py
import httpx
import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from app.config.settings import settings
from app.core.exceptions import AIServiceError

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.timeout = settings.OPENROUTER_TIMEOUT
        
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
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """OpenRouter completion API çağrısı"""
        
        model = model or settings.OPENROUTER_DEFAULT_MODEL
        max_tokens = max_tokens or settings.OPENROUTER_MAX_TOKENS
        temperature = temperature or settings.OPENROUTER_TEMPERATURE
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    raise AIServiceError(
                        f"OpenRouter API error: {response.status_code}",
                        details=error_data
                    )
                
                if stream:
                    return self._handle_stream_response(response)
                else:
                    return response.json()
                    
        except httpx.TimeoutException:
            raise AIServiceError("OpenRouter API timeout")
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise AIServiceError(f"OpenRouter API error: {str(e)}")
    
    async def create_embedding(
        self,
        text: str,
        model: str = None
    ) -> List[float]:
        """Text embedding oluşturma"""
        
        model = model or settings.OPENROUTER_EMBEDDING_MODEL
        
        payload = {
            "model": model,
            "input": text
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    raise AIServiceError(
                        f"OpenRouter Embedding API error: {response.status_code}",
                        details=error_data
                    )
                
                result = response.json()
                return result["data"][0]["embedding"]
                
        except Exception as e:
            logger.error(f"OpenRouter Embedding error: {str(e)}")
            raise AIServiceError(f"OpenRouter Embedding error: {str(e)}")
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streaming completion"""
        
        kwargs["stream"] = True
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": model or settings.OPENROUTER_DEFAULT_MODEL,
                    "messages": messages,
                    "stream": True,
                    **kwargs
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        
                        if data == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError):
                            continue
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Kullanılabilir model listesi"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()["data"]
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
            return []
    
    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Belirli model bilgileri"""
        models = await self.get_available_models()
        for model in models:
            if model["id"] == model_name:
                return model
        return None
```

#### AI Service Integration
```python
# app/services/ai_service.py
from typing import Dict, List, Optional, AsyncGenerator
from app.integrations.openrouter.client import OpenRouterClient
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.openrouter = OpenRouterClient()
    
    async def generate_response(
        self,
        chatbot_id: int,
        user_message: str,
        context: str = None,
        chat_history: List[Dict] = None,
        model: str = None
    ) -> Dict[str, Any]:
        """Chatbot response oluşturma"""
        
        # Model selection based on chatbot configuration
        chatbot_model = await self._get_chatbot_model(chatbot_id)
        selected_model = model or chatbot_model or settings.OPENROUTER_DEFAULT_MODEL
        
        # Message preparation
        messages = self._prepare_messages(
            user_message=user_message,
            context=context,
            chat_history=chat_history,
            chatbot_id=chatbot_id
        )
        
        try:
            # OpenRouter API call
            response = await self.openrouter.create_completion(
                messages=messages,
                model=selected_model,
                max_tokens=settings.OPENROUTER_MAX_TOKENS,
                temperature=settings.OPENROUTER_TEMPERATURE
            )
            
            # Response processing
            content = response["choices"][0]["message"]["content"]
            
            # Usage tracking
            usage = response.get("usage", {})
            
            return {
                "response": content,
                "model": selected_model,
                "tokens_used": usage.get("total_tokens", 0),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "cost_estimate": self._calculate_cost(usage, selected_model)
            }
            
        except Exception as e:
            logger.error(f"AI response generation failed: {str(e)}")
            raise
    
    async def generate_streaming_response(
        self,
        chatbot_id: int,
        user_message: str,
        context: str = None,
        chat_history: List[Dict] = None,
        model: str = None
    ) -> AsyncGenerator[str, None]:
        """Streaming response oluşturma"""
        
        chatbot_model = await self._get_chatbot_model(chatbot_id)
        selected_model = model or chatbot_model or settings.OPENROUTER_DEFAULT_MODEL
        
        messages = self._prepare_messages(
            user_message=user_message,
            context=context,
            chat_history=chat_history,
            chatbot_id=chatbot_id
        )
        
        async for chunk in self.openrouter.stream_completion(
            messages=messages,
            model=selected_model
        ):
            yield chunk
    
    async def create_embedding(self, text: str, model: str = None) -> List[float]:
        """Text embedding oluşturma"""
        embedding_model = model or settings.OPENROUTER_EMBEDDING_MODEL
        
        try:
            embedding = await self.openrouter.create_embedding(
                text=text,
                model=embedding_model
            )
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding creation failed: {str(e)}")
            raise
    
    def _prepare_messages(
        self,
        user_message: str,
        context: str = None,
        chat_history: List[Dict] = None,
        chatbot_id: int = None
    ) -> List[Dict[str, str]]:
        """Chat messages hazırlama"""
        
        messages = []
        
        # System message with chatbot personality
        system_message = self._get_system_message(chatbot_id, context)
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Chat history
        if chat_history:
            for msg in chat_history[-10:]:  # Son 10 mesaj
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _get_system_message(self, chatbot_id: int, context: str = None) -> str:
        """System message oluşturma"""
        base_system = "Sen yardımcı bir AI asistanısın. Kullanıcılara nazik ve bilgilendirici yanıtlar ver."
        
        if context:
            base_system += f"\n\nİlgili Bilgiler:\n{context}"
        
        # Chatbot-specific instructions
        # This would be fetched from database in real implementation
        
        return base_system
    
    async def _get_chatbot_model(self, chatbot_id: int) -> Optional[str]:
        """Chatbot için yapılandırılmış model"""
        # Database'den chatbot model preference getirme
        # Implementation details...
        return None
    
    def _calculate_cost(self, usage: Dict, model: str) -> float:
        """Token kullanımına göre maliyet hesaplama"""
        model_config = settings.OPENROUTER_MODELS.get(
            model.split("/")[-1], 
            {"cost_per_token": 0.000001}
        )
        
        total_tokens = usage.get("total_tokens", 0)
        cost_per_token = model_config["cost_per_token"]
        
        return total_tokens * cost_per_token
```

### 2.3 Model Management

#### Dynamic Model Selection
```python
# app/services/model_service.py
from typing import Dict, List, Optional
from app.integrations.openrouter.client import OpenRouterClient
from app.config.settings import settings

class ModelService:
    def __init__(self):
        self.openrouter = OpenRouterClient()
    
    async def get_best_model_for_task(self, task_type: str, complexity: str = "medium") -> str:
        """Task tipine göre en uygun model seçimi"""
        
        model_recommendations = {
            "general_chat": {
                "simple": "openai/gpt-3.5-turbo",
                "medium": "openai/gpt-3.5-turbo",
                "complex": "openai/gpt-4"
            },
            "technical_support": {
                "simple": "openai/gpt-3.5-turbo",
                "medium": "anthropic/claude-3-sonnet",
                "complex": "openai/gpt-4"
            },
            "creative_writing": {
                "simple": "openai/gpt-3.5-turbo",
                "medium": "anthropic/claude-3-sonnet",
                "complex": "openai/gpt-4"
            },
            "code_generation": {
                "simple": "openai/gpt-3.5-turbo",
                "medium": "openai/gpt-4",
                "complex": "openai/gpt-4"
            },
            "embedding": "openai/text-embedding-ada-002"
        }
        
        if task_type == "embedding":
            return model_recommendations["embedding"]
        
        return model_recommendations.get(task_type, {}).get(
            complexity, 
            settings.OPENROUTER_DEFAULT_MODEL
        )
    
    async def get_model_pricing(self) -> Dict[str, Dict]:
        """Model fiyatlandırma bilgileri"""
        available_models = await self.openrouter.get_available_models()
        
        pricing_info = {}
        for model in available_models:
            pricing_info[model["id"]] = {
                "input_cost": model.get("pricing", {}).get("prompt", 0),
                "output_cost": model.get("pricing", {}).get("completion", 0),
                "context_length": model.get("context_length", 4096),
                "description": model.get("description", "")
            }
        
        return pricing_info
    
    async def estimate_cost(
        self, 
        model: str, 
        prompt_tokens: int, 
        completion_tokens: int
    ) -> float:
        """Maliyet tahmini"""
        pricing = await self.get_model_pricing()
        
        if model not in pricing:
            return 0.0
        
        model_pricing = pricing[model]
        
        input_cost = (prompt_tokens / 1000) * model_pricing["input_cost"]
        output_cost = (completion_tokens / 1000) * model_pricing["output_cost"]
        
        return input_cost + output_cost
```

## 3. Supabase Yapılandırması

Supabase, MarkaMind'da authentication, database ve file storage için kullanılır.

### 3.1 Supabase Configuration

#### Environment Variables
```bash
# .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_DB_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
```

#### Settings Configuration
```python
# app/config/settings.py (addition)
class Settings(BaseSettings):
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_JWT_SECRET: str
    SUPABASE_DB_URL: str
    
    # Database Pool Settings
    SUPABASE_POOL_SIZE: int = 20
    SUPABASE_MAX_OVERFLOW: int = 30
    SUPABASE_POOL_TIMEOUT: int = 30
    
    # Storage Settings
    SUPABASE_STORAGE_BUCKET: str = "markamind-files"
    SUPABASE_MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
```

### 3.2 Supabase Client Implementation

#### Database Client
```python
# app/integrations/supabase/client.py
from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        # Supabase client for auth and realtime
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        
        # Service client for admin operations
        self.service_client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        
        # SQLAlchemy engine for direct database access
        self.engine = create_engine(
            settings.SUPABASE_DB_URL,
            poolclass=QueuePool,
            pool_size=settings.SUPABASE_POOL_SIZE,
            max_overflow=settings.SUPABASE_MAX_OVERFLOW,
            pool_timeout=settings.SUPABASE_POOL_TIMEOUT,
            pool_pre_ping=True
        )
        
        # Session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def get_database_session(self):
        """Database session factory"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    async def authenticate_user(self, email: str, password: str) -> dict:
        """Kullanıcı kimlik doğrulama"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return {
                    "success": True,
                    "user": response.user,
                    "session": response.session
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_user(self, email: str, password: str, metadata: dict = None) -> dict:
        """Yeni kullanıcı oluşturma"""
        try:
            response = self.service_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": metadata or {}
            })
            
            return {
                "success": True,
                "user": response.user
            }
            
        except Exception as e:
            logger.error(f"User creation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_jwt_token(self, token: str) -> dict:
        """JWT token doğrulama"""
        try:
            response = self.client.auth.get_user(token)
            
            if response.user:
                return {
                    "valid": True,
                    "user": response.user
                }
            else:
                return {
                    "valid": False,
                    "error": "Invalid token"
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def upload_file(self, bucket: str, file_path: str, file_data: bytes, content_type: str = None) -> dict:
        """Dosya yükleme"""
        try:
            response = self.client.storage.from_(bucket).upload(
                file_path,
                file_data,
                file_options={
                    "content-type": content_type or "application/octet-stream",
                    "cache-control": "3600"
                }
            )
            
            if response.get("error"):
                return {
                    "success": False,
                    "error": response["error"]["message"]
                }
            
            # Get public URL
            public_url = self.client.storage.from_(bucket).get_public_url(file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "public_url": public_url
            }
            
        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_file(self, bucket: str, file_path: str) -> dict:
        """Dosya silme"""
        try:
            response = self.client.storage.from_(bucket).remove([file_path])
            
            return {
                "success": True,
                "deleted_files": response
            }
            
        except Exception as e:
            logger.error(f"File deletion error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_file_url(self, bucket: str, file_path: str, expires_in: int = 3600) -> str:
        """Geçici dosya URL'i oluşturma"""
        try:
            response = self.client.storage.from_(bucket).create_signed_url(
                file_path,
                expires_in
            )
            
            return response.get("signedURL", "")
            
        except Exception as e:
            logger.error(f"URL generation error: {str(e)}")
            return ""

# Global instance
supabase_client = SupabaseClient()
```

#### Real-time Subscriptions
```python
# app/integrations/supabase/realtime.py
from typing import Callable, Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class SupabaseRealtimeManager:
    def __init__(self, client):
        self.client = client
        self.subscriptions = {}
    
    async def subscribe_to_table(
        self,
        table_name: str,
        event_type: str,  # INSERT, UPDATE, DELETE, *
        callback: Callable,
        filter_condition: str = None
    ) -> str:
        """Tablo değişikliklerini dinleme"""
        
        try:
            subscription_id = f"{table_name}_{event_type}_{len(self.subscriptions)}"
            
            # Supabase realtime subscription
            channel = self.client.channel(f"changes_{subscription_id}")
            
            def handle_change(payload):
                asyncio.create_task(callback(payload))
            
            channel.on(
                "postgres_changes",
                {
                    "event": event_type,
                    "schema": "public",
                    "table": table_name,
                    "filter": filter_condition
                },
                handle_change
            )
            
            channel.subscribe()
            
            self.subscriptions[subscription_id] = channel
            
            return subscription_id
            
        except Exception as e:
            logger.error(f"Realtime subscription error: {str(e)}")
            return None
    
    async def unsubscribe(self, subscription_id: str):
        """Subscription iptal etme"""
        if subscription_id in self.subscriptions:
            channel = self.subscriptions[subscription_id]
            channel.unsubscribe()
            del self.subscriptions[subscription_id]
    
    async def broadcast_message(self, channel_name: str, message: Dict[str, Any]):
        """Realtime mesaj broadcast"""
        try:
            channel = self.client.channel(channel_name)
            channel.send({
                "type": "broadcast",
                "event": "message",
                "payload": message
            })
            
        except Exception as e:
            logger.error(f"Broadcast error: {str(e)}")

# Global instance
realtime_manager = SupabaseRealtimeManager(supabase_client.client)
```

### 3.3 Row Level Security (RLS) Policies

#### Database Security Setup
```sql
-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE chatbots ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- User access policies
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id::text);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id::text);

-- Chatbot access policies
CREATE POLICY "Users can view own chatbots" ON chatbots
    FOR SELECT USING (auth.uid() = user_id::text);

CREATE POLICY "Users can create chatbots" ON chatbots
    FOR INSERT WITH CHECK (auth.uid() = user_id::text);

CREATE POLICY "Users can update own chatbots" ON chatbots
    FOR UPDATE USING (auth.uid() = user_id::text);

CREATE POLICY "Users can delete own chatbots" ON chatbots
    FOR DELETE USING (auth.uid() = user_id::text);

-- Conversation access policies
CREATE POLICY "Users can view chatbot conversations" ON conversations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM chatbots 
            WHERE chatbots.id = conversations.chatbot_id 
            AND chatbots.user_id::text = auth.uid()
        )
    );

-- Message access policies
CREATE POLICY "Users can view chatbot messages" ON messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversations 
            JOIN chatbots ON chatbots.id = conversations.chatbot_id
            WHERE conversations.id = messages.conversation_id 
            AND chatbots.user_id::text = auth.uid()
        )
    );
```

## 4. E-posta Servis Kurulumu

### 4.1 SMTP Configuration

#### Multiple Email Provider Support
```python
# app/config/settings.py (addition)
class Settings(BaseSettings):
    # Email Configuration
    EMAIL_PROVIDER: str = "smtp"  # smtp, sendgrid, mailgun, aws_ses
    
    # SMTP Settings
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    
    # SendGrid Settings  
    SENDGRID_API_KEY: Optional[str] = None
    
    # Mailgun Settings
    MAILGUN_API_KEY: Optional[str] = None
    MAILGUN_DOMAIN: Optional[str] = None
    
    # AWS SES Settings
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # Email Settings
    EMAIL_FROM: str = "noreply@markamind.com"
    EMAIL_FROM_NAME: str = "MarkaMind"
    EMAIL_TEMPLATES_DIR: str = "app/templates/emails"
    EMAIL_MAX_RETRIES: int = 3
    EMAIL_RETRY_DELAY: int = 5
```

### 4.2 Email Service Implementation

#### Base Email Service
```python
# app/services/email_service.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from jinja2 import Environment, FileSystemLoader
import httpx
import boto3
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class BaseEmailProvider(ABC):
    @abstractmethod
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: str = None,
        attachments: List[Dict] = None
    ) -> Dict[str, Any]:
        pass

class SMTPEmailProvider(BaseEmailProvider):
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_USE_TLS
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: str = None,
        attachments: List[Dict] = None
    ) -> Dict[str, Any]:
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            message["To"] = ", ".join(to_emails)
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    file_part = MIMEApplication(
                        attachment["content"],
                        Name=attachment["filename"]
                    )
                    file_part["Content-Disposition"] = f'attachment; filename="{attachment["filename"]}"'
                    message.attach(file_part)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.sendmail(settings.EMAIL_FROM, to_emails, message.as_string())
            
            return {
                "success": True,
                "provider": "smtp",
                "message_id": "smtp_message"
            }
            
        except Exception as e:
            logger.error(f"SMTP email error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

class SendGridEmailProvider(BaseEmailProvider):
    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.base_url = "https://api.sendgrid.com/v3/mail/send"
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: str = None,
        attachments: List[Dict] = None
    ) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": {
                "email": settings.EMAIL_FROM,
                "name": settings.EMAIL_FROM_NAME
            },
            "personalizations": [{
                "to": [{"email": email} for email in to_emails],
                "subject": subject
            }],
            "content": []
        }
        
        if text_content:
            payload["content"].append({
                "type": "text/plain",
                "value": text_content
            })
        
        payload["content"].append({
            "type": "text/html", 
            "value": html_content
        })
        
        # Add attachments
        if attachments:
            payload["attachments"] = []
            for attachment in attachments:
                import base64
                payload["attachments"].append({
                    "content": base64.b64encode(attachment["content"]).decode(),
                    "filename": attachment["filename"],
                    "type": attachment.get("content_type", "application/octet-stream")
                })
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 202:
                    return {
                        "success": True,
                        "provider": "sendgrid",
                        "message_id": response.headers.get("X-Message-Id")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"SendGrid error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"SendGrid email error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

class EmailService:
    def __init__(self):
        self.template_env = Environment(
            loader=FileSystemLoader(settings.EMAIL_TEMPLATES_DIR)
        )
        
        # Provider selection
        if settings.EMAIL_PROVIDER == "sendgrid":
            self.provider = SendGridEmailProvider()
        elif settings.EMAIL_PROVIDER == "smtp":
            self.provider = SMTPEmailProvider()
        else:
            self.provider = SMTPEmailProvider()  # Default fallback
    
    async def send_template_email(
        self,
        template_name: str,
        to_emails: List[str],
        subject: str,
        template_data: Dict[str, Any],
        attachments: List[Dict] = None
    ) -> Dict[str, Any]:
        """Template tabanlı email gönderme"""
        try:
            # Load and render template
            template = self.template_env.get_template(f"{template_name}.html")
            html_content = template.render(**template_data)
            
            # Try to load text version
            text_content = None
            try:
                text_template = self.template_env.get_template(f"{template_name}.txt")
                text_content = text_template.render(**template_data)
            except:
                pass
            
            return await self.provider.send_email(
                to_emails=to_emails,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                attachments=attachments
            )
            
        except Exception as e:
            logger.error(f"Template email error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_welcome_email(self, email: str, name: str) -> Dict[str, Any]:
        """Hoş geldin emaili"""
        return await self.send_template_email(
            template_name="welcome",
            to_emails=[email],
            subject="MarkaMind'a Hoş Geldiniz!",
            template_data={
                "name": name,
                "platform_url": "https://markamind.com"
            }
        )
    
    async def send_verification_email(self, email: str, verification_token: str) -> Dict[str, Any]:
        """Email doğrulama"""
        verification_url = f"https://markamind.com/verify-email?token={verification_token}"
        
        return await self.send_template_email(
            template_name="email_verification",
            to_emails=[email],
            subject="Email Adresinizi Doğrulayın",
            template_data={
                "verification_url": verification_url
            }
        )
    
    async def send_password_reset_email(self, email: str, reset_token: str) -> Dict[str, Any]:
        """Şifre sıfırlama"""
        reset_url = f"https://markamind.com/reset-password?token={reset_token}"
        
        return await self.send_template_email(
            template_name="password_reset",
            to_emails=[email],
            subject="Şifre Sıfırlama Talebi",
            template_data={
                "reset_url": reset_url
            }
        )
    
    async def send_report_email(
        self,
        recipients: List[str],
        subject: str,
        report_content: bytes,
        report_filename: str
    ) -> Dict[str, Any]:
        """Rapor emaili"""
        attachments = [{
            "content": report_content,
            "filename": report_filename,
            "content_type": "application/pdf"
        }]
        
        return await self.send_template_email(
            template_name="report",
            to_emails=recipients,
            subject=subject,
            template_data={
                "report_filename": report_filename
            },
            attachments=attachments
        )

# Global instance
email_service = EmailService()
```

### 4.3 Email Templates

#### Welcome Email Template
```html
<!-- app/templates/emails/welcome.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MarkaMind'a Hoş Geldiniz</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px 20px; }
        .button { display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 14px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MarkaMind</h1>
            <p>AI-Powered Chatbot Platform</p>
        </div>
        
        <div class="content">
            <h2>Merhaba {{ name }}!</h2>
            
            <p>MarkaMind'a hoş geldiniz! Hesabınız başarıyla oluşturuldu ve artık AI-powered chatbot'larınızı oluşturmaya başlayabilirsiniz.</p>
            
            <h3>Neler yapabilirsiniz:</h3>
            <ul>
                <li>🤖 Kendi chatbot'larınızı oluşturun</li>
                <li>📚 RAG sistemi ile eğitim veri yükleyin</li>
                <li>💬 Gerçek zamanlı sohbet deneyimi</li>
                <li>📊 Detaylı analytics ve raporlar</li>
                <li>🛒 Sanal mağaza entegrasyonu</li>
            </ul>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{{ platform_url }}" class="button">Platformu Keşfet</a>
            </p>
            
            <p>Herhangi bir sorunuz varsa, destek ekibimiz size yardımcı olmaktan memnuniyet duyar.</p>
        </div>
        
        <div class="footer">
            <p>&copy; 2024 MarkaMind. Tüm hakları saklıdır.</p>
            <p>Bu email otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
```

#### Text Version
```text
<!-- app/templates/emails/welcome.txt -->
MarkaMind'a Hoş Geldiniz!

Merhaba {{ name }},

MarkaMind'a hoş geldiniz! Hesabınız başarıyla oluşturuldu.

Neler yapabilirsiniz:
- Kendi chatbot'larınızı oluşturun
- RAG sistemi ile eğitim veri yükleyin  
- Gerçek zamanlı sohbet deneyimi
- Detaylı analytics ve raporlar
- Sanal mağaza entegrasyonu

Platformu keşfetmek için: {{ platform_url }}

Sorularınız için destek ekibimizle iletişime geçebilirsiniz.

MarkaMind Ekibi
© 2024 MarkaMind. Tüm hakları saklıdır.
```

## 5. Dosya Depolama Çözümleri

### 5.1 Multi-Provider File Storage

#### File Storage Interface
```python
# app/integrations/storage/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import os
from datetime import datetime

class BaseStorageProvider(ABC):
    @abstractmethod
    async def upload_file(
        self,
        file_path: str,
        file_data: bytes,
        content_type: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        pass
    
    @abstractmethod
    async def list_files(self, prefix: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        pass

# app/integrations/storage/supabase_storage.py
from app.integrations.storage.base import BaseStorageProvider
from app.integrations.supabase.client import supabase_client
from app.config.settings import settings

class SupabaseStorageProvider(BaseStorageProvider):
    def __init__(self):
        self.client = supabase_client
        self.bucket_name = settings.SUPABASE_STORAGE_BUCKET
    
    async def upload_file(
        self,
        file_path: str,
        file_data: bytes,
        content_type: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Supabase storage'a dosya yükleme"""
        
        # Add timestamp to prevent overwrite
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        base_name, extension = os.path.splitext(file_path)
        unique_path = f"{base_name}_{timestamp}{extension}"
        
        try:
            result = await self.client.upload_file(
                bucket=self.bucket_name,
                file_path=unique_path,
                file_data=file_data,
                content_type=content_type
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "file_path": unique_path,
                    "public_url": result["public_url"],
                    "size": len(file_data),
                    "content_type": content_type,
                    "metadata": metadata or {}
                }
            else:
                return {
                    "success": False,
                    "error": result["error"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def download_file(self, file_path: str) -> bytes:
        """Dosya indirme"""
        try:
            response = self.client.client.storage.from_(self.bucket_name).download(file_path)
            return response
        except Exception as e:
            raise Exception(f"File download error: {str(e)}")
    
    async def delete_file(self, file_path: str) -> bool:
        """Dosya silme"""
        try:
            result = await self.client.delete_file(self.bucket_name, file_path)
            return result["success"]
        except Exception:
            return False
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Geçici dosya URL'i"""
        try:
            return await self.client.get_file_url(self.bucket_name, file_path, expires_in)
        except Exception:
            return ""
    
    async def list_files(self, prefix: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        """Dosya listesi"""
        try:
            response = self.client.client.storage.from_(self.bucket_name).list(
                path=prefix,
                limit=limit
            )
            
            return [
                {
                    "name": file["name"],
                    "size": file.get("metadata", {}).get("size", 0),
                    "created_at": file.get("created_at"),
                    "updated_at": file.get("updated_at")
                }
                for file in response
            ]
        except Exception:
            return []
```

#### Local Storage Provider
```python
# app/integrations/storage/local_storage.py
import os
import shutil
from pathlib import Path
from app.integrations.storage.base import BaseStorageProvider
from app.config.settings import settings

class LocalStorageProvider(BaseStorageProvider):
    def __init__(self):
        self.base_path = Path(settings.UPLOAD_DIR)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(
        self,
        file_path: str,
        file_data: bytes,
        content_type: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Local storage'a dosya kaydetme"""
        try:
            full_path = self.base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'wb') as f:
                f.write(file_data)
            
            return {
                "success": True,
                "file_path": file_path,
                "public_url": f"/files/{file_path}",
                "size": len(file_data),
                "content_type": content_type,
                "metadata": metadata or {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def download_file(self, file_path: str) -> bytes:
        """Dosya okuma"""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(full_path, 'rb') as f:
            return f.read()
    
    async def delete_file(self, file_path: str) -> bool:
        """Dosya silme"""
        try:
            full_path = self.base_path / file_path
            if full_path.exists():
                os.remove(full_path)
            return True
        except Exception:
            return False
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Static file URL"""
        return f"/files/{file_path}"
    
    async def list_files(self, prefix: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        """Dosya listesi"""
        try:
            files = []
            search_path = self.base_path / prefix if prefix else self.base_path
            
            for file_path in search_path.rglob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "name": str(file_path.relative_to(self.base_path)),
                        "size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "updated_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                    
                    if len(files) >= limit:
                        break
            
            return files
            
        except Exception:
            return []
```

#### File Service Implementation
```python
# app/services/file_service.py
from typing import Dict, Any, List, Optional
from app.integrations.storage.supabase_storage import SupabaseStorageProvider
from app.integrations.storage.local_storage import LocalStorageProvider
from app.config.settings import settings
import mimetypes
import hashlib
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        # Storage provider selection
        if settings.ENVIRONMENT == "production":
            self.storage = SupabaseStorageProvider()
        else:
            self.storage = LocalStorageProvider()
        
        self.allowed_extensions = {
            'pdf', 'txt', 'docx', 'doc', 'md',
            'jpg', 'jpeg', 'png', 'gif', 'webp',
            'mp3', 'wav', 'mp4', 'avi', 'mov'
        }
        
        self.max_file_size = settings.SUPABASE_MAX_FILE_SIZE
    
    async def upload_training_file(
        self,
        chatbot_id: int,
        file_name: str,
        file_content: bytes,
        user_id: int
    ) -> Dict[str, Any]:
        """Eğitim dosyası yükleme"""
        
        # File validation
        validation_result = self._validate_file(file_name, file_content)
        if not validation_result["valid"]:
            return validation_result
        
        # Generate file path
        file_hash = hashlib.md5(file_content).hexdigest()[:8]
        extension = file_name.split('.')[-1].lower()
        file_path = f"training/{user_id}/{chatbot_id}/{file_hash}_{file_name}"
        
        # Content type detection
        content_type, _ = mimetypes.guess_type(file_name)
        
        # Upload file
        upload_result = await self.storage.upload_file(
            file_path=file_path,
            file_data=file_content,
            content_type=content_type,
            metadata={
                "chatbot_id": chatbot_id,
                "user_id": user_id,
                "original_filename": file_name,
                "file_hash": file_hash
            }
        )
        
        if upload_result["success"]:
            # Log file upload
            logger.info(f"Training file uploaded: {file_path} for chatbot {chatbot_id}")
        
        return upload_result
    
    async def upload_user_avatar(
        self,
        user_id: int,
        file_name: str,
        file_content: bytes
    ) -> Dict[str, Any]:
        """Kullanıcı avatar yükleme"""
        
        # Validate image file
        if not self._is_image_file(file_name):
            return {
                "success": False,
                "error": "Only image files are allowed for avatars"
            }
        
        # Generate file path
        extension = file_name.split('.')[-1].lower()
        file_path = f"avatars/{user_id}/avatar.{extension}"
        
        # Content type
        content_type, _ = mimetypes.guess_type(file_name)
        
        # Upload file
        return await self.storage.upload_file(
            file_path=file_path,
            file_data=file_content,
            content_type=content_type,
            metadata={
                "user_id": user_id,
                "type": "avatar"
            }
        )
    
    async def get_file_download_url(
        self,
        file_path: str,
        expires_in: int = 3600
    ) -> str:
        """Dosya indirme URL'i"""
        return await self.storage.get_file_url(file_path, expires_in)
    
    async def delete_file(self, file_path: str) -> bool:
        """Dosya silme"""
        try:
            result = await self.storage.delete_file(file_path)
            if result:
                logger.info(f"File deleted: {file_path}")
            return result
        except Exception as e:
            logger.error(f"File deletion error: {str(e)}")
            return False
    
    async def list_user_files(
        self,
        user_id: int,
        file_type: str = "training"
    ) -> List[Dict[str, Any]]:
        """Kullanıcı dosya listesi"""
        prefix = f"{file_type}/{user_id}/"
        return await self.storage.list_files(prefix=prefix)
    
    def _validate_file(self, file_name: str, file_content: bytes) -> Dict[str, Any]:
        """Dosya doğrulama"""
        
        # Size check
        if len(file_content) > self.max_file_size:
            return {
                "valid": False,
                "error": f"File size exceeds {self.max_file_size / (1024*1024):.1f}MB limit"
            }
        
        # Extension check
        extension = file_name.split('.')[-1].lower()
        if extension not in self.allowed_extensions:
            return {
                "valid": False,
                "error": f"File type {extension} is not allowed"
            }
        
        # Content validation
        if not self._validate_file_content(file_content, extension):
            return {
                "valid": False,
                "error": "Invalid file content"
            }
        
        return {"valid": True}
    
    def _is_image_file(self, file_name: str) -> bool:
        """Resim dosyası kontrolü"""
        image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        extension = file_name.split('.')[-1].lower()
        return extension in image_extensions
    
    def _validate_file_content(self, file_content: bytes, extension: str) -> bool:
        """Dosya içerik doğrulama"""
        
        # Basic magic number checks
        magic_numbers = {
            'pdf': b'%PDF',
            'png': b'\x89PNG',
            'jpg': b'\xff\xd8\xff',
            'jpeg': b'\xff\xd8\xff',
            'gif': b'GIF'
        }
        
        if extension in magic_numbers:
            magic = magic_numbers[extension]
            return file_content.startswith(magic)
        
        # Text files - basic UTF-8 check
        if extension in ['txt', 'md']:
            try:
                file_content.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
        
        return True

# Global instance
file_service = FileService()
```

### 5.2 File Processing Pipeline

#### Background File Processing
```python
# app/tasks/file_processing_tasks.py
from celery import current_task
from app.tasks.celery_app import celery_app
from app.services.file_service import file_service
from app.services.training_service import TrainingService
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_uploaded_file(self, file_path: str, chatbot_id: int, file_type: str):
    """Yüklenen dosyayı işleme"""
    
    try:
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'File validation...'}
        )
        
        # Download file content
        file_content = await file_service.storage.download_file(file_path)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 30, 'total': 100, 'status': 'Processing content...'}
        )
        
        # Process based on file type
        training_service = TrainingService()
        
        if file_type == 'pdf':
            result = await training_service.process_pdf_content(
                chatbot_id=chatbot_id,
                pdf_content=file_content,
                source_file=file_path
            )
        elif file_type in ['txt', 'md']:
            text_content = file_content.decode('utf-8')
            result = await training_service.process_text_content(
                chatbot_id=chatbot_id,
                text_content=text_content,
                source_file=file_path
            )
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 80, 'total': 100, 'status': 'Creating embeddings...'}
        )
        
        # Create embeddings
        embedding_result = await training_service.create_embeddings_for_chunks(
            chatbot_id=chatbot_id,
            chunk_ids=result["chunk_ids"]
        )
        
        self.update_state(
            state='SUCCESS',
            meta={
                'current': 100,
                'total': 100,
                'status': 'Completed',
                'result': {
                    **result,
                    **embedding_result
                }
            }
        )
        
        return {
            "success": True,
            "file_path": file_path,
            "chunks_created": result["chunks_created"],
            "embeddings_created": embedding_result["embeddings_created"]
        }
        
    except Exception as e:
        logger.error(f"File processing failed: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
```

Bu üçüncü taraf entegrasyon sistemi şunları sağlıyor:

✅ **OpenRouter API**: Multiple AI model desteği ile maliyet-efektif AI çözümü
✅ **Supabase**: Authentication, database ve real-time özellikler
✅ **Email Service**: Multiple provider desteği (SMTP, SendGrid, Mailgun)
✅ **File Storage**: Supabase Storage ve local storage seçenekleri
✅ **Security**: RLS policies ve JWT authentication
✅ **Scalability**: Provider değiştirme esnekliği
✅ **Monitoring**: Error handling ve logging

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "OpenRouter API entegrasyonunu tasarla", "status": "completed", "priority": "high", "id": "1"}, {"content": "Supabase yap\u0131land\u0131rmas\u0131n\u0131 planla", "status": "completed", "priority": "high", "id": "2"}, {"content": "E-posta servis kurulumunu tasarla", "status": "completed", "priority": "high", "id": "3"}, {"content": "Dosya depolama \u00e7\u00f6z\u00fcmlerini planla", "status": "completed", "priority": "high", "id": "4"}, {"content": "third-party-integrations.md dosyas\u0131n\u0131 olu\u015ftur", "status": "completed", "priority": "high", "id": "5"}]