-- ============================================================================
-- MarkaMind FastAPI Backend - Add Auth Columns to Existing Users Table
-- File: add_auth_columns.sql
-- Purpose: Adds necessary columns to existing users table without conflicts
-- ============================================================================

-- First, let's see what columns already exist in users table
DO $$
DECLARE
    col_exists boolean;
BEGIN
    -- Check if oauth_provider column exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'oauth_provider'
    ) INTO col_exists;

    IF NOT col_exists THEN
        ALTER TABLE public.users ADD COLUMN oauth_provider TEXT;
        RAISE NOTICE 'Added oauth_provider column';
    ELSE
        RAISE NOTICE 'oauth_provider column already exists';
    END IF;

    -- Check if oauth_provider_id column exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'oauth_provider_id'
    ) INTO col_exists;

    IF NOT col_exists THEN
        ALTER TABLE public.users ADD COLUMN oauth_provider_id TEXT;
        RAISE NOTICE 'Added oauth_provider_id column';
    ELSE
        RAISE NOTICE 'oauth_provider_id column already exists';
    END IF;

    -- Check if auth_method column exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'auth_method'
    ) INTO col_exists;

    IF NOT col_exists THEN
        ALTER TABLE public.users ADD COLUMN auth_method TEXT DEFAULT 'password';
        RAISE NOTICE 'Added auth_method column';
    ELSE
        RAISE NOTICE 'auth_method column already exists';
    END IF;

    -- Check if email_verified column exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'email_verified'
    ) INTO col_exists;

    IF NOT col_exists THEN
        ALTER TABLE public.users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added email_verified column';
    ELSE
        RAISE NOTICE 'email_verified column already exists';
    END IF;

    -- Check if is_active column exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'is_active'
    ) INTO col_exists;

    IF NOT col_exists THEN
        ALTER TABLE public.users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
        RAISE NOTICE 'Added is_active column';
    ELSE
        RAISE NOTICE 'is_active column already exists';
    END IF;

    -- Check if last_login column exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'users'
        AND column_name = 'last_login'
    ) INTO col_exists;

    IF NOT col_exists THEN
        ALTER TABLE public.users ADD COLUMN last_login TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE 'Added last_login column';
    ELSE
        RAISE NOTICE 'last_login column already exists';
    END IF;

END $$;

-- ============================================================================
-- Create additional auth tables that don't conflict with existing structure
-- ============================================================================

-- OAuth providers table
CREATE TABLE IF NOT EXISTS public.oauth_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    client_id TEXT, -- Made optional, will be set via environment variables
    client_secret TEXT,
    authorize_url TEXT NOT NULL,
    token_url TEXT NOT NULL,
    userinfo_url TEXT,
    default_scopes TEXT[] DEFAULT ARRAY[]::TEXT[],
    extra_params JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User sessions table
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    refresh_token_jti TEXT UNIQUE,
    access_token_jti TEXT,
    client_ip INET,
    user_agent TEXT,
    device_fingerprint TEXT,
    country_code TEXT,
    city TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    logout_reason TEXT,
    suspicious_activity BOOLEAN DEFAULT FALSE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Password reset tokens table
CREATE TABLE IF NOT EXISTS public.password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    token_hash TEXT UNIQUE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    client_ip INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() + INTERVAL '1 hour'),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Email verification tokens table
CREATE TABLE IF NOT EXISTS public.email_verification_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    token_hash TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    client_ip INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() + INTERVAL '24 hours'),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User audit log table
CREATE TABLE IF NOT EXISTS public.user_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    event_description TEXT,
    event_data JSONB DEFAULT '{}'::jsonb,
    client_ip INET,
    user_agent TEXT,
    request_method TEXT,
    request_path TEXT,
    risk_level TEXT DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    is_suspicious BOOLEAN DEFAULT FALSE,
    country_code TEXT,
    city TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API keys table
CREATE TABLE IF NOT EXISTS public.api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    key_hash TEXT UNIQUE NOT NULL,
    key_prefix TEXT NOT NULL,
    scopes TEXT[] DEFAULT ARRAY[]::TEXT[],
    last_used_at TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    rate_limit_per_minute INTEGER DEFAULT 60,
    rate_limit_per_hour INTEGER DEFAULT 3600,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- Add indexes for performance
-- ============================================================================

-- Users table indexes (only add if they don't exist)
CREATE INDEX IF NOT EXISTS idx_users_oauth_provider ON public.users(oauth_provider);
CREATE INDEX IF NOT EXISTS idx_users_oauth_provider_id ON public.users(oauth_provider_id);
CREATE INDEX IF NOT EXISTS idx_users_auth_method ON public.users(auth_method);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON public.users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_email_verified ON public.users(email_verified);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON public.users(last_login);

-- Other table indexes
CREATE INDEX IF NOT EXISTS idx_oauth_providers_name ON public.oauth_providers(provider_name);
CREATE INDEX IF NOT EXISTS idx_oauth_providers_active ON public.oauth_providers(is_active);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON public.user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON public.user_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON public.user_sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_password_reset_user_id ON public.password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_token_hash ON public.password_reset_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_password_reset_expires ON public.password_reset_tokens(expires_at);

CREATE INDEX IF NOT EXISTS idx_email_verification_user_id ON public.email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_token_hash ON public.email_verification_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_email_verification_expires ON public.email_verification_tokens(expires_at);

CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON public.user_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_event_type ON public.user_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON public.user_audit_log(created_at);

CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON public.api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON public.api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON public.api_keys(is_active);

-- ============================================================================
-- Add default OAuth providers
-- ============================================================================

INSERT INTO public.oauth_providers (provider_name, display_name, client_id, authorize_url, token_url, userinfo_url, default_scopes)
VALUES
    (
        'google',
        'Google',
        'your_google_client_id_here', -- Replace with actual client ID from .env
        'https://accounts.google.com/o/oauth2/v2/auth',
        'https://oauth2.googleapis.com/token',
        'https://www.googleapis.com/oauth2/v2/userinfo',
        ARRAY['openid', 'email', 'profile']
    ),
    (
        'github',
        'GitHub',
        'your_github_client_id_here', -- Replace with actual client ID from .env
        'https://github.com/login/oauth/authorize',
        'https://github.com/login/oauth/access_token',
        'https://api.github.com/user',
        ARRAY['user:email']
    )
ON CONFLICT (provider_name) DO NOTHING;

-- ============================================================================
-- Add constraints safely
-- ============================================================================

DO $$
BEGIN
    -- Try to add unique constraint for OAuth users
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'unique_oauth_user'
    ) THEN
        ALTER TABLE public.users
        ADD CONSTRAINT unique_oauth_user UNIQUE(oauth_provider, oauth_provider_id);
        RAISE NOTICE 'Added unique OAuth user constraint';
    ELSE
        RAISE NOTICE 'unique_oauth_user constraint already exists';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Could not add unique_oauth_user constraint: %', SQLERRM;
END $$;

-- ============================================================================
-- Completion message
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Auth tables migration completed successfully!';
    RAISE NOTICE 'Added missing columns to existing users table';
    RAISE NOTICE 'Created additional auth tables: oauth_providers, user_sessions, password_reset_tokens, email_verification_tokens, user_audit_log, api_keys';
    RAISE NOTICE 'Applied indexes and constraints';
END $$;