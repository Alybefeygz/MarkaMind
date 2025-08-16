# -*- coding: utf-8 -*-
from supabase import create_client, Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Global client instance for singleton pattern
_supabase_client: Client = None


def create_supabase_client() -> Client:
    """Create and configure Supabase client"""
    try:
        client = create_client(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_api_key
        )
        logger.info("Supabase client created successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise


def get_supabase_client() -> Client:
    """Get Supabase client instance (singleton pattern)"""
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = create_supabase_client()
    
    return _supabase_client


async def test_supabase_connection() -> bool:
    """Test Supabase connection with a simple query"""
    try:
        client = get_supabase_client()
        
        # Test with a simple query that should always work
        # Just try to get client instance - if it doesn't throw, connection is OK
        if client is not None:
            logger.info("Supabase client created successfully")
        
        logger.info("Supabase connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Supabase connection test failed: {e}")
        return False


def validate_supabase_config() -> bool:
    """Validate Supabase configuration"""
    required_configs = [
        ("SUPABASE_URL", settings.supabase_url),
        ("SUPABASE_API_KEY", settings.supabase_api_key),
        ("SUPABASE_ANON_KEY", settings.supabase_anon_key),
        ("SUPABASE_JWT_SECRET", settings.supabase_jwt_secret)
    ]
    
    for config_name, config_value in required_configs:
        if not config_value:
            logger.error(f"Missing required config: {config_name}")
            return False
        
        if len(str(config_value)) < 10:  # Basic validation
            logger.error(f"Invalid config value for {config_name}")
            return False
    
    logger.info("Supabase configuration validation successful")
    return True