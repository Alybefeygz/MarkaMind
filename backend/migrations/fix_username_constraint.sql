-- Fix username constraint in users table
-- This fixes the malformed regex pattern

-- Drop the existing malformed constraint
DO $$
BEGIN
    -- Try to drop any existing username constraints
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname LIKE '%username%' AND conrelid = 'public.users'::regclass
    ) THEN
        ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_username_check;
        ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_username_key;
        RAISE NOTICE 'Dropped existing username constraints';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error dropping constraints: %', SQLERRM;
END $$;

-- Add correct username constraint
DO $$
BEGIN
    -- Add unique constraint for username
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'users_username_unique'
    ) THEN
        ALTER TABLE public.users
        ADD CONSTRAINT users_username_unique UNIQUE (username);
        RAISE NOTICE 'Added unique constraint for username';
    END IF;

    -- Add check constraint for username format
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'users_username_format'
    ) THEN
        ALTER TABLE public.users
        ADD CONSTRAINT users_username_format
        CHECK (username ~ '^[a-zA-Z0-9_-]{3,30}$');
        RAISE NOTICE 'Added username format constraint';
    END IF;
END $$;

-- Create index for username if it doesn't exist
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);

-- Verify the fix
DO $$
DECLARE
    constraint_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO constraint_count
    FROM pg_constraint
    WHERE conrelid = 'public.users'::regclass
    AND conname IN ('users_username_unique', 'users_username_format');

    RAISE NOTICE 'Username constraints created: %', constraint_count;

    IF constraint_count = 2 THEN
        RAISE NOTICE 'SUCCESS: Username constraints fixed!';
    ELSE
        RAISE NOTICE 'WARNING: Some constraints may be missing';
    END IF;
END $$;