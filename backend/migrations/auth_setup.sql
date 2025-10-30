-- ============================================
-- Authentication Setup Migration
-- ============================================
-- Bu script'i Supabase SQL Editor'de çalıştır
-- ============================================

-- 1. UUID Extension (zaten var ama emin olmak için)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. pgcrypto Extension (token hashing için)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 3. Users tablosuna auth field'ları ekle (eğer yoksa)
-- Not: Users tablosu zaten var, sadece eksik field'ları ekliyoruz

DO $$
BEGIN
    -- password_hash field ekle
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'password_hash'
    ) THEN
        ALTER TABLE users ADD COLUMN password_hash TEXT;
    END IF;

    -- email_verified field ekle
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'email_verified'
    ) THEN
        ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT false;
    END IF;

    -- email_confirmed_at field ekle
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'email_confirmed_at'
    ) THEN
        ALTER TABLE users ADD COLUMN email_confirmed_at TIMESTAMP WITH TIME ZONE;
    END IF;

    -- last_login field ekle
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'last_login'
    ) THEN
        ALTER TABLE users ADD COLUMN last_login TIMESTAMP WITH TIME ZONE;
    END IF;

    -- is_active field ekle
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'is_active'
    ) THEN
        ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;

    -- username field ekle
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'username'
    ) THEN
        ALTER TABLE users ADD COLUMN username TEXT UNIQUE;
        ALTER TABLE users ADD CONSTRAINT username_format CHECK (username ~ '^[a-zA-Z0-9_-]{3,30}$');
    END IF;

    -- role field ekle
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'role'
    ) THEN
        ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin'));
    END IF;
END $$;

-- 4. Email Verification Tokens tablosunu kontrol et/oluştur
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    is_used BOOLEAN DEFAULT false,
    used_at TIMESTAMP WITH TIME ZONE,
    client_ip INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() + INTERVAL '24 hours'),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index'ler
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_user_id ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_token_hash ON email_verification_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_expires_at ON email_verification_tokens(expires_at);

-- 5. Password Reset Tokens tablosunu kontrol et/oluştur
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    is_used BOOLEAN DEFAULT false,
    used_at TIMESTAMP WITH TIME ZONE,
    client_ip INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() + INTERVAL '1 hour'),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index'ler
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token_hash ON password_reset_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);

-- 6. User Audit Log tablosunu kontrol et/oluştur
CREATE TABLE IF NOT EXISTS user_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    event_description TEXT,
    event_data JSONB DEFAULT '{}'::jsonb,
    client_ip INET,
    user_agent TEXT,
    request_method TEXT,
    request_path TEXT,
    risk_level TEXT DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    is_suspicious BOOLEAN DEFAULT false,
    country_code TEXT,
    city TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index'ler
CREATE INDEX IF NOT EXISTS idx_user_audit_log_user_id ON user_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_user_audit_log_event_type ON user_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_user_audit_log_created_at ON user_audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_user_audit_log_client_ip ON user_audit_log(client_ip);
CREATE INDEX IF NOT EXISTS idx_user_audit_log_is_suspicious ON user_audit_log(is_suspicious);

-- 7. Expired token'ları temizleme fonksiyonu
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS void AS $$
BEGIN
    -- Expired email verification tokens
    DELETE FROM email_verification_tokens
    WHERE expires_at < NOW() AND is_used = false;

    -- Expired password reset tokens
    DELETE FROM password_reset_tokens
    WHERE expires_at < NOW() AND is_used = false;
END;
$$ LANGUAGE plpgsql;

-- 8. Otomatik token temizleme (pg_cron extension gerekli)
-- Not: Supabase'de pg_cron extension'ı enable etmen gerekebilir
-- Alternatif: Backend'den cron job ile çağır
-- SELECT cron.schedule('cleanup-expired-tokens', '0 * * * *', 'SELECT cleanup_expired_tokens()');

-- 9. Updated_at trigger fonksiyonu
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Users tablosu için trigger
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 10. Row Level Security (RLS) Policies
-- Users tablosu için RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Kullanıcı kendi profilini görebilir
CREATE POLICY "Users can view their own profile"
    ON users FOR SELECT
    USING (auth.uid() = id);

-- Kullanıcı kendi profilini güncelleyebilir
CREATE POLICY "Users can update their own profile"
    ON users FOR UPDATE
    USING (auth.uid() = id);

-- Email verification tokens RLS
ALTER TABLE email_verification_tokens ENABLE ROW LEVEL SECURITY;

-- Password reset tokens RLS
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;

-- Audit log RLS (sadece kendi loglarını görebilir)
ALTER TABLE user_audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own audit logs"
    ON user_audit_log FOR SELECT
    USING (auth.uid() = user_id);

-- ============================================
-- Migration tamamlandı! 🎉
-- ============================================
