-- ============================================================================
-- MarkaMind Backend - Add Username Column to Users Table
-- File: username_add_user_table.sql
-- Purpose: Adds username field to existing users table with proper constraints
-- ============================================================================

-- Add username column to users table
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS username TEXT;

-- Add unique constraint for username
DO $$
BEGIN
    -- Check if constraint already exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'users_username_unique'
    ) THEN
        ALTER TABLE public.users
        ADD CONSTRAINT users_username_unique UNIQUE (username);
        RAISE NOTICE 'Added unique constraint for username';
    ELSE
        RAISE NOTICE 'Username unique constraint already exists';
    END IF;
END $$;

-- Add check constraint for username format (alphanumeric, underscore, hyphen)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'users_username_format'
    ) THEN
        ALTER TABLE public.users
        ADD CONSTRAINT users_username_format
        CHECK (username ~ '^[a-zA-Z0-9_-]{3,30}$');
        RAISE NOTICE 'Added username format constraint';
    ELSE
        RAISE NOTICE 'Username format constraint already exists';
    END IF;
END $$;

-- Create index for username (for faster lookups)
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);

-- Add comment to describe the username column
COMMENT ON COLUMN public.users.username IS 'Unique username for the user (3-30 chars, alphanumeric, underscore, hyphen)';

-- ============================================================================
-- Optional: Generate usernames for existing users (if any)
-- ============================================================================

-- Function to generate username from email
CREATE OR REPLACE FUNCTION generate_username_from_email(email_address TEXT)
RETURNS TEXT AS $$
DECLARE
    base_username TEXT;
    final_username TEXT;
    counter INTEGER := 0;
BEGIN
    -- Extract username part from email (before @)
    base_username := split_part(email_address, '@', 1);

    -- Clean up the username (remove invalid characters)
    base_username := regexp_replace(base_username, '[^a-zA-Z0-9_-]', '', 'g');

    -- Ensure minimum length
    IF length(base_username) < 3 THEN
        base_username := 'user' || base_username;
    END IF;

    -- Ensure maximum length
    IF length(base_username) > 25 THEN
        base_username := left(base_username, 25);
    END IF;

    final_username := base_username;

    -- Check for uniqueness and add number suffix if needed
    WHILE EXISTS (SELECT 1 FROM public.users WHERE username = final_username) LOOP
        counter := counter + 1;
        final_username := base_username || counter;

        -- Ensure total length doesn't exceed 30 chars
        IF length(final_username) > 30 THEN
            base_username := left(base_username, 30 - length(counter::TEXT));
            final_username := base_username || counter;
        END IF;
    END LOOP;

    RETURN final_username;
END;
$$ LANGUAGE plpgsql;

-- Update existing users without username
DO $$
DECLARE
    user_record RECORD;
    new_username TEXT;
BEGIN
    -- Loop through users without username
    FOR user_record IN
        SELECT id, email FROM public.users
        WHERE username IS NULL
    LOOP
        -- Generate username from email
        new_username := generate_username_from_email(user_record.email);

        -- Update user with generated username
        UPDATE public.users
        SET username = new_username
        WHERE id = user_record.id;

        RAISE NOTICE 'Generated username "%" for user %', new_username, user_record.email;
    END LOOP;
END $$;

-- ============================================================================
-- Validation and Statistics
-- ============================================================================

-- Show statistics after migration
DO $$
DECLARE
    total_users INTEGER;
    users_with_username INTEGER;
    users_without_username INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_users FROM public.users;
    SELECT COUNT(*) INTO users_with_username FROM public.users WHERE username IS NOT NULL;
    SELECT COUNT(*) INTO users_without_username FROM public.users WHERE username IS NULL;

    RAISE NOTICE '=== USERNAME MIGRATION STATISTICS ===';
    RAISE NOTICE 'Total users: %', total_users;
    RAISE NOTICE 'Users with username: %', users_with_username;
    RAISE NOTICE 'Users without username: %', users_without_username;

    IF users_without_username = 0 THEN
        RAISE NOTICE 'SUCCESS: All users have usernames!';
    ELSE
        RAISE NOTICE 'WARNING: % users still need usernames', users_without_username;
    END IF;
END $$;

-- ============================================================================
-- Utility Functions for Username Management
-- ============================================================================

-- Function to check if username is available
CREATE OR REPLACE FUNCTION is_username_available(username_to_check TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check format first
    IF username_to_check !~ '^[a-zA-Z0-9_-]{3,30}$' THEN
        RETURN FALSE;
    END IF;

    -- Check uniqueness
    RETURN NOT EXISTS (
        SELECT 1 FROM public.users
        WHERE username = username_to_check
    );
END;
$$ LANGUAGE plpgsql;

-- Function to suggest available usernames
CREATE OR REPLACE FUNCTION suggest_usernames(base_username TEXT)
RETURNS TEXT[] AS $$
DECLARE
    suggestions TEXT[] := '{}';
    candidate TEXT;
    i INTEGER;
BEGIN
    -- Clean base username
    base_username := regexp_replace(base_username, '[^a-zA-Z0-9_-]', '', 'g');
    base_username := left(base_username, 25);

    -- Generate 5 suggestions
    FOR i IN 1..5 LOOP
        candidate := base_username || i;
        IF is_username_available(candidate) THEN
            suggestions := array_append(suggestions, candidate);
        END IF;
    END LOOP;

    RETURN suggestions;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Completion Message
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '=== USERNAME MIGRATION COMPLETED ===';
    RAISE NOTICE 'Added username column with:';
    RAISE NOTICE '- UNIQUE constraint';
    RAISE NOTICE '- Format validation (3-30 chars, alphanumeric + _ -)';
    RAISE NOTICE '- Index for fast lookups';
    RAISE NOTICE '- Auto-generated usernames for existing users';
    RAISE NOTICE '- Utility functions: is_username_available(), suggest_usernames()';
    RAISE NOTICE '======================================';
END $$;