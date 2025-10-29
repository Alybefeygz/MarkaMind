-- users tablosuna avatar alanları ekle
  ALTER TABLE public.users
  ADD COLUMN avatar_url TEXT,
  ADD COLUMN avatar_type TEXT DEFAULT 'gravatar' CHECK (avatar_type IN ('upload', 'gravatar', 'initials')),
  ADD COLUMN avatar_updated_at TIMESTAMP WITH TIME ZONE;

  -- Index ekle
  CREATE INDEX idx_users_avatar_type ON public.users(avatar_type);