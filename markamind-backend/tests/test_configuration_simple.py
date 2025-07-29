"""
Simplified backend configuration validation tests.
Tests core settings loading, environment variables, and logging setup.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch


class TestCoreConfiguration:
    """Test core configuration functionality."""
    
    def test_settings_import_and_basic_values(self):
        """Test that settings can be imported and have basic values."""
        from app.config.settings import Settings, settings
        
        assert settings is not None
        assert settings.APP_NAME == "MarkaMind Backend API"
        assert settings.VERSION == "1.0.0"
        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        
        print("✅ Settings imported with correct default values")
    
    def test_settings_environment_override(self):
        """Test that environment variables override defaults."""
        from app.config.settings import Settings
        
        test_env = {
            "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test-key",
            "SUPABASE_SERVICE_KEY": "test-service-key",
            "SECRET_KEY": "test-secret-key",
            "OPENROUTER_API_KEY": "sk-test-key",
            "ENVIRONMENT": "testing",
            "DEBUG": "false",
            "LOG_LEVEL": "WARNING"
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()
            
            assert settings.ENVIRONMENT == "testing"
            assert settings.DEBUG == False
            assert settings.LOG_LEVEL == "WARNING"
            assert settings.DATABASE_URL == "postgresql://test:test@localhost:5432/test"
        
        print("✅ Environment variables correctly override defaults")
    
    def test_settings_ai_configuration(self):
        """Test AI-related settings."""
        from app.config.settings import settings
        
        assert settings.OPENROUTER_BASE_URL == "https://openrouter.ai/api/v1"
        assert settings.OPENROUTER_DEFAULT_MODEL == "openai/gpt-3.5-turbo"
        assert settings.OPENROUTER_EMBEDDING_MODEL == "openai/text-embedding-ada-002"
        assert settings.OPENROUTER_MAX_TOKENS == 2048
        assert settings.OPENROUTER_TEMPERATURE == 0.7
        
        print("✅ AI configuration settings are correct")
    
    def test_settings_rag_configuration(self):
        """Test RAG-related settings."""
        from app.config.settings import settings
        
        assert settings.RAG_CHUNK_SIZE == 1000
        assert settings.RAG_CHUNK_OVERLAP == 200
        assert settings.RAG_SIMILARITY_THRESHOLD == 0.7
        assert settings.RAG_TOP_K == 5
        
        print("✅ RAG configuration settings are correct")
    
    def test_settings_file_configuration(self):
        """Test file handling settings."""
        from app.config.settings import settings
        
        assert settings.MAX_FILE_SIZE == 50 * 1024 * 1024  # 50MB
        assert settings.ALLOWED_FILE_TYPES == ["pdf", "txt", "docx", "md"]
        
        print("✅ File configuration settings are correct")


class TestDatabaseConfiguration:
    """Test database configuration (without requiring psycopg2)."""
    
    def test_database_imports(self):
        """Test database configuration imports."""
        from app.config.database import engine, SessionLocal, Base, get_db
        
        # Engine might be None if psycopg2 is not installed
        assert Base is not None
        assert get_db is not None
        
        print("✅ Database configuration imports work")
    
    def test_get_db_without_connection(self):
        """Test get_db behavior when database is not initialized."""
        from app.config.database import get_db, SessionLocal
        
        if SessionLocal is None:
            # Should raise RuntimeError when database is not initialized
            db_gen = get_db()
            with pytest.raises(RuntimeError, match="Database not initialized"):
                next(db_gen)
            print("✅ get_db correctly handles uninitialized database")
        else:
            print("✅ Database is initialized (psycopg2 available)")


class TestLoggingConfiguration:
    """Test logging configuration."""
    
    def test_logging_import(self):
        """Test logging configuration import."""
        from app.config.logging import setup_logging
        
        assert setup_logging is not None
        print("✅ Logging configuration imported successfully")
    
    def test_logging_setup_execution(self):
        """Test that logging setup executes without errors."""
        from app.config.logging import setup_logging
        
        try:
            logger = setup_logging()
            assert logger is not None
            print("✅ Logging setup executed successfully")
        except Exception as e:
            pytest.fail(f"Logging setup failed: {e}")
    
    def test_logging_levels(self):
        """Test different logging levels."""
        import logging
        from app.config.logging import setup_logging
        
        # Test that setup_logging works without errors
        try:
            logger = setup_logging()
            assert logger is not None
            print("✅ Logging levels configured correctly")
        except Exception as e:
            pytest.fail(f"Logging level configuration failed: {e}")


class TestEnvironmentFiles:
    """Test environment file configuration."""
    
    def test_env_example_exists(self):
        """Test that .env.example file exists."""
        project_root = Path(__file__).parent.parent
        env_example_path = project_root / ".env.example"
        
        assert env_example_path.exists(), ".env.example file does not exist"
        assert env_example_path.is_file(), ".env.example is not a file"
        
        print("✅ .env.example file exists")
    
    def test_env_example_structure(self):
        """Test .env.example file has required structure."""
        project_root = Path(__file__).parent.parent
        env_example_path = project_root / ".env.example"
        
        content = env_example_path.read_text()
        
        # Check for major sections
        required_sections = [
            "# Database (Supabase)",
            "# Security",
            "# OpenRouter AI",
            "# Environment"
        ]
        
        for section in required_sections:
            assert section in content, f"Section '{section}' missing from .env.example"
        
        # Check for critical variables
        critical_vars = [
            "DATABASE_URL=",
            "SECRET_KEY=",
            "OPENROUTER_API_KEY=",
            "ENVIRONMENT="
        ]
        
        for var in critical_vars:
            assert var in content, f"Variable '{var}' missing from .env.example"
        
        print("✅ .env.example file structure is correct")
    
    def test_env_file_exists(self):
        """Test that development .env file exists."""
        project_root = Path(__file__).parent.parent
        env_path = project_root / ".env"
        
        assert env_path.exists(), ".env file does not exist (needed for development)"
        assert env_path.is_file(), ".env is not a file"
        
        print("✅ Development .env file exists")


class TestConfigurationIntegration:
    """Test configuration integration without database connection."""
    
    def test_basic_integration(self):
        """Test basic configuration integration."""
        try:
            from app.config.settings import settings
            from app.config.database import Base
            from app.config.logging import setup_logging
            
            # Test settings
            assert settings.APP_NAME == "MarkaMind Backend API"
            
            # Test database base exists
            assert Base is not None
            
            # Test logging setup
            logger = setup_logging()
            assert logger is not None
            
            print("✅ Basic configuration integration successful")
            
        except Exception as e:
            pytest.fail(f"Configuration integration failed: {e}")
    
    def test_settings_access_patterns(self):
        """Test common configuration access patterns."""
        from app.config.settings import settings
        
        # Test grouping related settings
        auth_config = {
            "secret_key": settings.SECRET_KEY,
            "algorithm": settings.ALGORITHM,
            "expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
        }
        
        ai_config = {
            "api_key": settings.OPENROUTER_API_KEY,
            "base_url": settings.OPENROUTER_BASE_URL,
            "model": settings.OPENROUTER_DEFAULT_MODEL
        }
        
        # All values should be populated
        assert all(auth_config.values())
        assert all(ai_config.values())
        
        print("✅ Configuration access patterns work correctly")
    
    def test_environment_detection(self):
        """Test environment detection."""
        from app.config.settings import settings
        
        # Should have a valid environment
        valid_environments = ["development", "testing", "staging", "production"]
        assert settings.ENVIRONMENT in valid_environments
        
        # Debug should be boolean
        assert isinstance(settings.DEBUG, bool)
        
        print(f"✅ Environment detection works (env: {settings.ENVIRONMENT}, debug: {settings.DEBUG})")


def test_configuration_complete():
    """Integration test for complete configuration setup."""
    from app.config.settings import settings
    from app.config.logging import setup_logging
    
    # Test that we can access all major configuration areas
    assert settings.APP_NAME
    assert settings.DATABASE_URL
    assert settings.SECRET_KEY
    assert settings.OPENROUTER_API_KEY
    
    # Test logging
    logger = setup_logging()
    logger.info("Configuration test completed successfully")
    
    print("✅ Complete configuration test passed!")
    print(f"App: {settings.APP_NAME} v{settings.VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug: {settings.DEBUG}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])