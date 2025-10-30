"""
Supabase Client Configuration
"""
from supabase import create_client, Client
from app.config import settings
from functools import lru_cache


@lru_cache()
def get_supabase_client() -> Client:
    """
    Supabase client'ı oluşturur ve döner
    Singleton pattern ile sadece bir kere oluşturulur
    """
    supabase: Client = create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_API_KEY
    )
    return supabase


@lru_cache()
def get_supabase_admin_client() -> Client:
    """
    Supabase admin client (service role key ile)
    RLS bypass için kullanılır
    """
    supabase_admin: Client = create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_API_KEY  # Service role key
    )
    return supabase_admin


# Global instances
supabase = get_supabase_client()
supabase_admin = get_supabase_admin_client()
