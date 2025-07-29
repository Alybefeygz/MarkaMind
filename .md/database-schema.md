# MarkaMind Database Schema

## Genel Bakış

MarkaMind platformu PostgreSQL veritabanı kullanarak, kullanıcılar, chatbot'lar, RAG sistemi, abonelikler ve analitik verileri yönetir. Bu dokümantasyon tüm tablo şemalarını, ilişkileri ve performans optimizasyonlarını detaylandırır.

## Database Configuration

```sql
-- PostgreSQL 15+ with extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
-- CREATE EXTENSION IF NOT EXISTS "vector"; -- pgvector for future vector similarity
```

## 1. Core Tables

### 1.1 users
**Açıklama:** Platform kullanıcılarının temel bilgileri

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(255),
    phone VARCHAR(20),
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_uuid ON users(uuid);
CREATE INDEX idx_users_verification_token ON users(email_verification_token);
CREATE INDEX idx_users_reset_token ON users(password_reset_token);
CREATE INDEX idx_users_company ON users(company_name);
```

### 1.2 chatbots
**Açıklama:** Kullanıcı chatbot'larının ana tablosu

```sql
CREATE TABLE chatbots (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) DEFAULT 'general',
    language VARCHAR(10) DEFAULT 'tr',
    status VARCHAR(20) DEFAULT 'draft', -- draft, active, inactive, training
    
    -- Settings JSON
    settings JSONB DEFAULT '{}' NOT NULL,
    
    -- Appearance JSON
    appearance JSONB DEFAULT '{}' NOT NULL,
    
    -- Performance metrics
    message_count INTEGER DEFAULT 0,
    unique_users_count INTEGER DEFAULT 0,
    average_response_time DECIMAL(5,3) DEFAULT 0.0,
    satisfaction_score DECIMAL(3,2) DEFAULT 0.0,
    
    -- Training info
    last_trained TIMESTAMP,
    training_data_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_chatbots_user ON chatbots(user_id);
CREATE INDEX idx_chatbots_uuid ON chatbots(uuid);
CREATE INDEX idx_chatbots_status ON chatbots(status);
CREATE INDEX idx_chatbots_category ON chatbots(category);
CREATE INDEX idx_chatbots_name_trgm ON chatbots USING gin(name gin_trgm_ops);
CREATE INDEX idx_chatbots_settings ON chatbots USING gin(settings);
```

## 2. Training & RAG System Tables

### 2.1 training_data
**Açıklama:** Chatbot eğitim verilerinin saklandığı tablo

```sql
CREATE TABLE training_data (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    chatbot_id INTEGER NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL, -- pdf, text, url, manual
    filename VARCHAR(255),
    original_filename VARCHAR(255),
    file_path VARCHAR(500),
    file_size INTEGER,
    content_preview TEXT,
    metadata JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, processed, failed
    processing_log TEXT,
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_training_data_chatbot ON training_data(chatbot_id);
CREATE INDEX idx_training_data_type ON training_data(type);
CREATE INDEX idx_training_data_status ON training_data(status);
CREATE INDEX idx_training_data_filename ON training_data(filename);
CREATE INDEX idx_training_data_metadata ON training_data USING gin(metadata);
```

### 2.2 rag_chunks
**Açıklama:** RAG sistemi için metin parçaları

```sql
CREATE TABLE rag_chunks (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    chatbot_id INTEGER NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    training_data_id INTEGER NOT NULL REFERENCES training_data(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    text_hash VARCHAR(64) NOT NULL, -- For duplicate detection
    source_type VARCHAR(20) NOT NULL,
    chunk_size INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_rag_chunks_chatbot ON rag_chunks(chatbot_id);
CREATE INDEX idx_rag_chunks_training_data ON rag_chunks(training_data_id);
CREATE INDEX idx_rag_chunks_hash ON rag_chunks(text_hash);
CREATE INDEX idx_rag_chunks_source ON rag_chunks(source_type);
CREATE INDEX idx_rag_chunks_metadata ON rag_chunks USING gin(metadata);
CREATE INDEX idx_rag_chunks_composite ON rag_chunks(chatbot_id, chunk_index);
```

### 2.3 rag_embeddings
**Açıklama:** RAG chunk'ların embedding vektörleri

```sql
CREATE TABLE rag_embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL REFERENCES rag_chunks(id) ON DELETE CASCADE UNIQUE,
    embedding DECIMAL(8,6)[] NOT NULL, -- Array of floats for embedding vector
    model VARCHAR(100) NOT NULL,
    dimension INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_rag_embeddings_chunk ON rag_embeddings(chunk_id);
CREATE INDEX idx_rag_embeddings_model ON rag_embeddings(model);
-- Future: Vector similarity index with pgvector
-- CREATE INDEX idx_rag_embeddings_vector ON rag_embeddings USING ivfflat (embedding vector_cosine_ops);
```

## 3. Conversation & Chat Tables

### 3.1 conversations
**Açıklama:** Sohbet oturumları

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    chatbot_id INTEGER NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255), -- Can be anonymous
    user_ip INET,
    user_agent TEXT,
    
    -- Conversation metadata
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- active, ended, abandoned
    
    -- Quality metrics
    satisfaction_score INTEGER, -- 1-5 rating
    satisfaction_feedback TEXT,
    
    -- Context data
    context_data JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_conversations_chatbot ON conversations(chatbot_id);
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_started ON conversations(started_at);
CREATE INDEX idx_conversations_satisfaction ON conversations(satisfaction_score);
```

### 3.2 messages
**Açıklama:** Sohbet mesajları

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    message_type VARCHAR(10) NOT NULL, -- user, bot, system
    content TEXT NOT NULL,
    
    -- Bot response metadata
    response_time_ms INTEGER,
    confidence_score DECIMAL(3,2),
    sources_used JSONB DEFAULT '[]', -- RAG sources
    context_used TEXT,
    
    -- Message metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_type ON messages(message_type);
CREATE INDEX idx_messages_created ON messages(created_at);
CREATE INDEX idx_messages_confidence ON messages(confidence_score);
CREATE INDEX idx_messages_response_time ON messages(response_time_ms);
CREATE INDEX idx_messages_content_search ON messages USING gin(to_tsvector('turkish', content));
```

## 4. Subscription & Billing Tables

### 4.1 packages
**Açıklama:** Abonelik paketleri

```sql
CREATE TABLE packages (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL, -- basic, professional, enterprise
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Pricing
    monthly_price DECIMAL(10,2) NOT NULL,
    yearly_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'TRY',
    
    -- Limits
    chatbot_limit INTEGER NOT NULL,
    monthly_message_limit INTEGER NOT NULL,
    training_data_mb_limit INTEGER NOT NULL,
    api_calls_per_day_limit INTEGER NOT NULL,
    concurrent_users_limit INTEGER NOT NULL,
    data_retention_days INTEGER NOT NULL,
    
    -- Features JSON
    features JSONB DEFAULT '{}' NOT NULL,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_packages_code ON packages(code);
CREATE INDEX idx_packages_active ON packages(is_active);
CREATE INDEX idx_packages_features ON packages USING gin(features);
```

### 4.2 subscriptions
**Açıklama:** Kullanıcı abonelikleri

```sql
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    package_id INTEGER NOT NULL REFERENCES packages(id),
    
    status VARCHAR(20) DEFAULT 'active', -- active, cancelled, expired, suspended
    billing_cycle VARCHAR(10) NOT NULL, -- monthly, yearly
    
    -- Billing dates
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    next_billing_date TIMESTAMP,
    
    -- Pricing
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'TRY',
    
    -- Payment info
    payment_method_id VARCHAR(255),
    last_payment_date TIMESTAMP,
    
    -- Usage tracking
    usage_data JSONB DEFAULT '{}',
    
    auto_renewal BOOLEAN DEFAULT TRUE,
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_package ON subscriptions(package_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_billing_date ON subscriptions(next_billing_date);
CREATE INDEX idx_subscriptions_period ON subscriptions(current_period_start, current_period_end);
```

### 4.3 usage_logs
**Açıklama:** Kullanım istatistikleri günlük kayıtları

```sql
CREATE TABLE usage_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- Usage metrics
    messages_sent INTEGER DEFAULT 0,
    api_calls_made INTEGER DEFAULT 0,
    data_processed_mb DECIMAL(8,2) DEFAULT 0,
    active_chatbots INTEGER DEFAULT 0,
    unique_users_served INTEGER DEFAULT 0,
    
    -- Performance metrics
    average_response_time DECIMAL(5,3) DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, date)
);

-- Indexes
CREATE INDEX idx_usage_logs_user_date ON usage_logs(user_id, date);
CREATE INDEX idx_usage_logs_date ON usage_logs(date);
```

## 5. Virtual Store Tables

### 5.1 virtual_stores
**Açıklama:** Kullanıcı sanal mağazaları

```sql
CREATE TABLE virtual_stores (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Store settings
    settings JSONB DEFAULT '{}' NOT NULL,
    theme VARCHAR(50) DEFAULT 'modern',
    logo_url VARCHAR(500),
    
    -- Store metadata
    status VARCHAR(20) DEFAULT 'active',
    total_products INTEGER DEFAULT 0,
    total_chatbots INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_virtual_stores_user ON virtual_stores(user_id);
CREATE INDEX idx_virtual_stores_status ON virtual_stores(status);
CREATE INDEX idx_virtual_stores_settings ON virtual_stores USING gin(settings);
```

### 5.2 store_products
**Açıklama:** Sanal mağaza ürünleri

```sql
CREATE TABLE store_products (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    store_id INTEGER NOT NULL REFERENCES virtual_stores(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Product details
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'TRY',
    category VARCHAR(100),
    sku VARCHAR(100),
    stock INTEGER DEFAULT 0,
    
    -- Media
    images JSONB DEFAULT '[]',
    
    -- Product specifications
    specifications JSONB DEFAULT '{}',
    tags TEXT[],
    
    -- Chatbot assignment
    assigned_chatbot_id INTEGER REFERENCES chatbots(id),
    custom_greeting TEXT,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_store_products_store ON store_products(store_id);
CREATE INDEX idx_store_products_category ON store_products(category);
CREATE INDEX idx_store_products_sku ON store_products(sku);
CREATE INDEX idx_store_products_chatbot ON store_products(assigned_chatbot_id);
CREATE INDEX idx_store_products_active ON store_products(is_active);
CREATE INDEX idx_store_products_name_search ON store_products USING gin(to_tsvector('turkish', name));
CREATE INDEX idx_store_products_tags ON store_products USING gin(tags);
```

## 6. Analytics & Monitoring Tables

### 6.1 analytics_events
**Açıklama:** Analitik olayları

```sql
CREATE TABLE analytics_events (
    id SERIAL PRIMARY KEY,
    chatbot_id INTEGER NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- message_sent, conversation_started, satisfaction_rated
    event_data JSONB DEFAULT '{}',
    
    -- Event context
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp partitioning
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE analytics_events_y2024m01 PARTITION OF analytics_events
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Indexes
CREATE INDEX idx_analytics_events_chatbot ON analytics_events(chatbot_id);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_created ON analytics_events(created_at);
CREATE INDEX idx_analytics_events_session ON analytics_events(session_id);
```

### 6.2 performance_metrics
**Açıklama:** Performans metrikleri günlük toplamları

```sql
CREATE TABLE performance_metrics (
    id SERIAL PRIMARY KEY,
    chatbot_id INTEGER NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- Conversation metrics
    total_conversations INTEGER DEFAULT 0,
    completed_conversations INTEGER DEFAULT 0,
    abandoned_conversations INTEGER DEFAULT 0,
    
    -- Message metrics
    total_messages INTEGER DEFAULT 0,
    average_response_time DECIMAL(5,3) DEFAULT 0,
    
    -- Quality metrics
    average_satisfaction DECIMAL(3,2) DEFAULT 0,
    total_ratings INTEGER DEFAULT 0,
    
    -- Error metrics
    error_count INTEGER DEFAULT 0,
    timeout_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(chatbot_id, date)
);

-- Indexes
CREATE INDEX idx_performance_metrics_chatbot_date ON performance_metrics(chatbot_id, date);
CREATE INDEX idx_performance_metrics_date ON performance_metrics(date);
```

## 7. System Tables

### 7.1 api_keys
**Açıklama:** Kullanıcı API anahtarları

```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    key_prefix VARCHAR(20) NOT NULL,
    
    -- Permissions and limits
    permissions JSONB DEFAULT '[]' NOT NULL,
    rate_limit INTEGER DEFAULT 1000,
    allowed_ips INET[],
    
    -- Usage tracking
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_prefix ON api_keys(key_prefix);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
```

### 7.2 webhooks
**Açıklama:** Webhook konfigürasyonları

```sql
CREATE TABLE webhooks (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    
    -- Configuration
    events TEXT[] NOT NULL,
    secret VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    
    -- Retry configuration
    max_retries INTEGER DEFAULT 3,
    retry_delay INTEGER DEFAULT 5000,
    
    -- Statistics
    total_deliveries INTEGER DEFAULT 0,
    successful_deliveries INTEGER DEFAULT 0,
    failed_deliveries INTEGER DEFAULT 0,
    last_triggered TIMESTAMP,
    last_success TIMESTAMP,
    last_failure TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_webhooks_user ON webhooks(user_id);
CREATE INDEX idx_webhooks_active ON webhooks(active);
CREATE INDEX idx_webhooks_events ON webhooks USING gin(events);
```

### 7.3 system_logs
**Açıklama:** Sistem logları

```sql
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(10) NOT NULL, -- DEBUG, INFO, WARNING, ERROR
    logger VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    
    -- Context data
    user_id INTEGER REFERENCES users(id),
    chatbot_id INTEGER REFERENCES chatbots(id),
    request_id UUID,
    
    -- Log data
    extra_data JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create monthly partitions for logs
CREATE TABLE system_logs_y2024m01 PARTITION OF system_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Indexes
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_logger ON system_logs(logger);
CREATE INDEX idx_system_logs_created ON system_logs(created_at);
CREATE INDEX idx_system_logs_user ON system_logs(user_id);
CREATE INDEX idx_system_logs_request ON system_logs(request_id);
```

## 8. Background Jobs Tables

### 8.1 job_queue
**Açıklama:** Celery job kuyruğu takibi

```sql
CREATE TABLE job_queue (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    
    -- Job context
    user_id INTEGER REFERENCES users(id),
    chatbot_id INTEGER REFERENCES chatbots(id),
    
    -- Job data
    args JSONB DEFAULT '[]',
    kwargs JSONB DEFAULT '{}',
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed, retrying
    progress INTEGER DEFAULT 0,
    result JSONB,
    error_message TEXT,
    
    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_completion TIMESTAMP,
    
    -- Retry logic
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3
);

-- Indexes
CREATE INDEX idx_job_queue_task_id ON job_queue(task_id);
CREATE INDEX idx_job_queue_status ON job_queue(status);
CREATE INDEX idx_job_queue_user ON job_queue(user_id);
CREATE INDEX idx_job_queue_chatbot ON job_queue(chatbot_id);
CREATE INDEX idx_job_queue_created ON job_queue(created_at);
```

## 9. Table Relationships

### ERD Overview
```
users (1) ──┬── (N) chatbots (1) ──┬── (N) training_data (1) ── (N) rag_chunks (1) ── (1) rag_embeddings
            │                      ├── (N) conversations (1) ── (N) messages
            │                      ├── (N) analytics_events
            │                      └── (N) performance_metrics
            │
            ├── (1) subscriptions (N) ── (1) packages
            ├── (N) usage_logs
            ├── (1) virtual_stores (1) ── (N) store_products (N) ──── (1) chatbots
            ├── (N) api_keys
            ├── (N) webhooks
            └── (N) job_queue
```

### Foreign Key Constraints

```sql
-- Core relationships
ALTER TABLE chatbots ADD CONSTRAINT fk_chatbots_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE training_data ADD CONSTRAINT fk_training_data_chatbot 
    FOREIGN KEY (chatbot_id) REFERENCES chatbots(id) ON DELETE CASCADE;

ALTER TABLE rag_chunks ADD CONSTRAINT fk_rag_chunks_chatbot 
    FOREIGN KEY (chatbot_id) REFERENCES chatbots(id) ON DELETE CASCADE;

ALTER TABLE rag_chunks ADD CONSTRAINT fk_rag_chunks_training_data 
    FOREIGN KEY (training_data_id) REFERENCES training_data(id) ON DELETE CASCADE;

ALTER TABLE rag_embeddings ADD CONSTRAINT fk_rag_embeddings_chunk 
    FOREIGN KEY (chunk_id) REFERENCES rag_chunks(id) ON DELETE CASCADE;

-- Conversation relationships
ALTER TABLE conversations ADD CONSTRAINT fk_conversations_chatbot 
    FOREIGN KEY (chatbot_id) REFERENCES chatbots(id) ON DELETE CASCADE;

ALTER TABLE messages ADD CONSTRAINT fk_messages_conversation 
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;

-- Subscription relationships
ALTER TABLE subscriptions ADD CONSTRAINT fk_subscriptions_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE subscriptions ADD CONSTRAINT fk_subscriptions_package 
    FOREIGN KEY (package_id) REFERENCES packages(id);
```

## 10. Performance Optimizations

### 10.1 Indexing Strategy

```sql
-- Composite indexes for common queries
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX idx_analytics_events_chatbot_type_created ON analytics_events(chatbot_id, event_type, created_at);
CREATE INDEX idx_usage_logs_user_date_desc ON usage_logs(user_id, date DESC);

-- Partial indexes for active records
CREATE INDEX idx_chatbots_active_user ON chatbots(user_id) WHERE status = 'active';
CREATE INDEX idx_subscriptions_active_user ON subscriptions(user_id) WHERE status = 'active';

-- GIN indexes for JSONB columns
CREATE INDEX idx_chatbots_settings_gin ON chatbots USING gin(settings);
CREATE INDEX idx_training_data_metadata_gin ON training_data USING gin(metadata);
CREATE INDEX idx_rag_chunks_metadata_gin ON rag_chunks USING gin(metadata);

-- Full-text search indexes
CREATE INDEX idx_messages_content_fts ON messages USING gin(to_tsvector('turkish', content));
CREATE INDEX idx_store_products_search ON store_products USING gin(
    to_tsvector('turkish', name || ' ' || COALESCE(description, ''))
);
```

### 10.2 Partitioning Strategy

```sql
-- Time-based partitioning for analytics_events
CREATE TABLE analytics_events_y2024m02 PARTITION OF analytics_events
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE analytics_events_y2024m03 PARTITION OF analytics_events
FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- Auto-partition creation function
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name text, start_date date)
RETURNS void AS $$
DECLARE
    partition_name text;
    end_date date;
BEGIN
    partition_name := table_name || '_y' || EXTRACT(year FROM start_date) || 'm' || 
                     LPAD(EXTRACT(month FROM start_date)::text, 2, '0');
    end_date := start_date + INTERVAL '1 month';
    
    EXECUTE format('CREATE TABLE %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
                   partition_name, table_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;
```

### 10.3 Query Optimization Views

```sql
-- Chatbot performance summary view
CREATE VIEW chatbot_performance_summary AS
SELECT 
    c.id,
    c.name,
    c.user_id,
    COUNT(DISTINCT conv.id) as total_conversations,
    COUNT(m.id) as total_messages,
    AVG(m.response_time_ms) as avg_response_time,
    AVG(conv.satisfaction_score) as avg_satisfaction,
    MAX(conv.started_at) as last_conversation
FROM chatbots c
LEFT JOIN conversations conv ON c.id = conv.chatbot_id
LEFT JOIN messages m ON conv.id = m.conversation_id AND m.message_type = 'bot'
WHERE c.status = 'active'
GROUP BY c.id, c.name, c.user_id;

-- User usage summary view
CREATE VIEW user_usage_summary AS
SELECT 
    u.id as user_id,
    u.email,
    s.package_id,
    p.name as package_name,
    COUNT(DISTINCT c.id) as active_chatbots,
    COALESCE(ul.messages_sent, 0) as monthly_messages,
    COALESCE(ul.api_calls_made, 0) as monthly_api_calls
FROM users u
LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active'
LEFT JOIN packages p ON s.package_id = p.id
LEFT JOIN chatbots c ON u.id = c.user_id AND c.status = 'active'
LEFT JOIN usage_logs ul ON u.id = ul.user_id AND ul.date = CURRENT_DATE
GROUP BY u.id, u.email, s.package_id, p.name, ul.messages_sent, ul.api_calls_made;
```

## 11. Migration Strategy

### 11.1 Alembic Configuration

```python
# alembic/env.py
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.models import Base  # Import all models
from app.config.settings import settings

def run_migrations():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        {"sqlalchemy.url": settings.DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()
```

### 11.2 Migration Phases

```sql
-- Phase 1: Core tables (users, chatbots, conversations)
-- Migration: 001_create_core_tables.py

-- Phase 2: Training and RAG system
-- Migration: 002_create_training_rag_tables.py

-- Phase 3: Subscription system
-- Migration: 003_create_subscription_tables.py

-- Phase 4: Virtual store
-- Migration: 004_create_virtual_store_tables.py

-- Phase 5: Analytics and monitoring
-- Migration: 005_create_analytics_tables.py

-- Phase 6: System tables (API keys, webhooks, jobs)
-- Migration: 006_create_system_tables.py

-- Phase 7: Performance indexes and optimizations
-- Migration: 007_add_performance_indexes.py

-- Phase 8: Partitioning setup
-- Migration: 008_setup_partitioning.py
```

### 11.3 Data Migration Scripts

```python
# scripts/migrate_existing_data.py
from sqlalchemy.orm import Session
from app.database import engine
from app.models import *

def migrate_user_data():
    """Migrate existing user data with data validation"""
    with Session(engine) as db:
        # Data migration logic
        pass

def create_default_packages():
    """Create default subscription packages"""
    packages_data = [
        {
            "code": "basic",
            "name": "Temel Paket",
            "monthly_price": 99.00,
            "yearly_price": 990.00,
            "chatbot_limit": 3,
            "monthly_message_limit": 1000,
            # ... other limits
        },
        # ... other packages
    ]
    
    with Session(engine) as db:
        for package_data in packages_data:
            package = Package(**package_data)
            db.add(package)
        db.commit()
```

### 11.4 Backup and Recovery Strategy

```sql
-- Full database backup
pg_dump -h localhost -U postgres -d markamind > backup_full_$(date +%Y%m%d).sql

-- Incremental backup with WAL
pg_basebackup -h localhost -U postgres -D /backup/base -Ft -z -P

-- Point-in-time recovery setup
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
wal_level = replica
```

## 12. Database Monitoring

### 12.1 Performance Monitoring Queries

```sql
-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage statistics
SELECT 
    indexrelname as index_name,
    relname as table_name,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;

-- Slow queries monitoring
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 20;
```

### 12.2 Health Check Views

```sql
-- Database health check
CREATE VIEW db_health_check AS
SELECT 
    'connection_count' as metric,
    COUNT(*) as value
FROM pg_stat_activity
UNION ALL
SELECT 
    'active_connections',
    COUNT(*) 
FROM pg_stat_activity 
WHERE state = 'active'
UNION ALL
SELECT 
    'database_size',
    pg_database_size(current_database());
```

Bu database schema MarkaMind platformunun tüm gereksinimlerini karşılayacak şekilde tasarlanmıştır. PostgreSQL'in gelişmiş özelliklerini kullanarak performans, ölçeklenebilirlik ve veri bütünlüğünü sağlar.