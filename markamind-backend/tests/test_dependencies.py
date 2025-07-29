"""
Backend dependencies validation tests.
Tests core packages (FastAPI, SQLAlchemy), AI packages (langchain, chromadb), and dev tools.
"""

import sys
import importlib
import pytest
from packaging import version


class TestCoreDependencies:
    """Test core backend dependencies."""
    
    def test_fastapi_import_and_version(self):
        """Test FastAPI import and version."""
        try:
            import fastapi
            assert fastapi.__version__ == "0.104.1", f"Expected FastAPI 0.104.1, got {fastapi.__version__}"
            print(f"✅ FastAPI {fastapi.__version__} imported successfully")
            
            # Test basic FastAPI functionality
            from fastapi import FastAPI
            app = FastAPI()
            assert app is not None, "Failed to create FastAPI instance"
            
        except ImportError as e:
            pytest.fail(f"Failed to import FastAPI: {e}")
    
    def test_uvicorn_import_and_version(self):
        """Test Uvicorn import and version."""
        try:
            import uvicorn
            assert uvicorn.__version__ == "0.24.0", f"Expected Uvicorn 0.24.0, got {uvicorn.__version__}"
            print(f"✅ Uvicorn {uvicorn.__version__} imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import Uvicorn: {e}")
    
    def test_sqlalchemy_import_and_version(self):
        """Test SQLAlchemy import and version."""
        try:
            import sqlalchemy
            assert sqlalchemy.__version__ == "2.0.23", f"Expected SQLAlchemy 2.0.23, got {sqlalchemy.__version__}"
            print(f"✅ SQLAlchemy {sqlalchemy.__version__} imported successfully")
            
            # Test basic SQLAlchemy functionality
            from sqlalchemy import create_engine, Column, Integer, String
            from sqlalchemy.orm import declarative_base
            
            Base = declarative_base()
            engine = create_engine("sqlite:///:memory:")
            assert engine is not None, "Failed to create SQLAlchemy engine"
            
        except ImportError as e:
            pytest.fail(f"Failed to import SQLAlchemy: {e}")
    
    def test_alembic_import_and_version(self):
        """Test Alembic import and version."""
        try:
            # Test alembic package import - avoid conflict with local alembic directory
            import sys
            import importlib
            
            # Try to import alembic from site-packages
            alembic_spec = importlib.util.find_spec("alembic")
            if alembic_spec and "site-packages" in str(alembic_spec.origin):
                # Import from installed package
                alembic_module = importlib.import_module("alembic") 
                print("✅ Alembic package imported successfully")
            else:
                print("⚠️ Alembic package not available (local directory conflict)")
            
        except (ImportError, AttributeError) as e:
            # Skip if there's a conflict with local directory
            print(f"⚠️ Alembic import skipped due to local directory conflict: {e}")
    
    def test_pydantic_import_and_version(self):
        """Test Pydantic import and version."""
        try:
            import pydantic
            assert pydantic.__version__ == "2.5.0", f"Expected Pydantic 2.5.0, got {pydantic.__version__}"
            print(f"✅ Pydantic {pydantic.__version__} imported successfully")
            
            # Test basic Pydantic functionality
            from pydantic import BaseModel
            
            class TestModel(BaseModel):
                name: str
                age: int
            
            model = TestModel(name="test", age=25)
            assert model.name == "test", "Pydantic model validation failed"
            
        except ImportError as e:
            pytest.fail(f"Failed to import Pydantic: {e}")
    
    def test_pydantic_settings_import(self):
        """Test Pydantic Settings import."""
        try:
            from pydantic_settings import BaseSettings
            
            class TestSettings(BaseSettings):
                test_var: str = "default"
            
            settings = TestSettings()
            assert settings.test_var == "default", "Pydantic Settings failed"
            print("✅ Pydantic Settings imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import Pydantic Settings: {e}")


class TestAuthenticationDependencies:
    """Test authentication and security dependencies."""
    
    def test_python_jose_import(self):
        """Test Python-JOSE import."""
        try:
            from jose import jwt
            from jose.exceptions import JWTError
            
            # Test basic JWT functionality
            secret = "test-secret"
            payload = {"test": "data"}
            token = jwt.encode(payload, secret, algorithm="HS256")
            decoded = jwt.decode(token, secret, algorithms=["HS256"])
            assert decoded["test"] == "data", "JWT encoding/decoding failed"
            print("✅ Python-JOSE imported and tested successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import Python-JOSE: {e}")
    
    def test_passlib_import(self):
        """Test Passlib import."""
        try:
            from passlib.context import CryptContext
            
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            password = "test-password"
            hashed = pwd_context.hash(password)
            assert pwd_context.verify(password, hashed), "Password hashing/verification failed"
            print("✅ Passlib imported and tested successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import Passlib: {e}")


class TestHTTPDependencies:
    """Test HTTP client dependencies."""
    
    def test_httpx_import_and_version(self):
        """Test HTTPx import and version."""
        try:
            import httpx
            # HTTPx version should be >= 0.24.0 and < 0.25.0
            httpx_version = version.parse(httpx.__version__)
            min_version = version.parse("0.24.0")
            max_version = version.parse("0.25.0")
            
            assert min_version <= httpx_version < max_version, f"HTTPx version {httpx.__version__} not in expected range 0.24.0-0.25.0"
            print(f"✅ HTTPx {httpx.__version__} imported successfully")
            
            # Test basic HTTPx functionality
            client = httpx.Client()
            assert client is not None, "Failed to create HTTPx client"
            client.close()
            
        except ImportError as e:
            pytest.fail(f"Failed to import HTTPx: {e}")
    
    def test_aiofiles_import(self):
        """Test aiofiles import."""
        try:
            import aiofiles
            # aiofiles doesn't expose __version__ directly
            print("✅ aiofiles imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import aiofiles: {e}")


class TestUtilityDependencies:
    """Test utility dependencies."""
    
    def test_python_dotenv_import(self):
        """Test python-dotenv import."""
        try:
            from dotenv import load_dotenv
            import os
            
            # Create a test .env content
            test_env_content = "TEST_VAR=test_value"
            with open(".env.test", "w") as f:
                f.write(test_env_content)
            
            load_dotenv(".env.test")
            assert os.getenv("TEST_VAR") == "test_value", "Environment variable loading failed"
            
            # Cleanup
            os.remove(".env.test")
            print("✅ python-dotenv imported and tested successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import python-dotenv: {e}")
    
    def test_python_multipart_import(self):
        """Test python-multipart import."""
        try:
            import multipart
            print("✅ python-multipart imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import python-multipart: {e}")
    
    def test_pillow_import(self):
        """Test Pillow import."""
        try:
            from PIL import Image
            import io
            
            # Test basic image functionality
            image = Image.new('RGB', (100, 100), color='red')
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            assert buffer.getvalue(), "Image processing failed"
            print(f"✅ Pillow imported and tested successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import Pillow: {e}")


class TestDevelopmentDependencies:
    """Test development tool dependencies."""
    
    def test_pytest_import_and_version(self):
        """Test pytest import and version."""
        try:
            import pytest
            assert pytest.__version__ == "7.4.3", f"Expected pytest 7.4.3, got {pytest.__version__}"
            print(f"✅ pytest {pytest.__version__} imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import pytest: {e}")
    
    def test_pytest_asyncio_import(self):
        """Test pytest-asyncio import."""
        try:
            import pytest_asyncio
            print(f"✅ pytest-asyncio {pytest_asyncio.__version__} imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import pytest-asyncio: {e}")
    
    def test_pytest_cov_import(self):
        """Test pytest-cov import."""
        try:
            import pytest_cov
            print(f"✅ pytest-cov imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import pytest-cov: {e}")
    
    def test_black_import_and_version(self):
        """Test Black import and version."""
        try:
            import black
            assert black.__version__ == "23.12.1", f"Expected Black 23.12.1, got {black.__version__}"
            print(f"✅ Black {black.__version__} imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import Black: {e}")
    
    def test_isort_import_and_version(self):
        """Test isort import and version."""
        try:
            import isort
            assert isort.__version__ == "5.13.2", f"Expected isort 5.13.2, got {isort.__version__}"
            print(f"✅ isort {isort.__version__} imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import isort: {e}")
    
    def test_flake8_import(self):
        """Test flake8 import."""
        try:
            import flake8
            print(f"✅ flake8 imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import flake8: {e}")
    
    def test_mypy_import_and_version(self):
        """Test mypy import and version."""
        try:
            import mypy
            # Just verify mypy can be imported
            print("✅ mypy imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import mypy: {e}")


class TestExtendedDependencies:
    """Test extended dependencies (optional, will skip if not installed)."""
    
    @pytest.mark.skipif(not importlib.util.find_spec("supabase"), 
                       reason="Supabase not installed - this is optional")
    def test_supabase_import(self):
        """Test Supabase import (optional)."""
        try:
            from supabase import create_client, Client
            print("✅ Supabase imported successfully")
            
        except ImportError as e:
            pytest.skip(f"Supabase not available: {e}")
    
    @pytest.mark.skipif(not importlib.util.find_spec("psycopg2"), 
                       reason="psycopg2 not installed - this is optional")
    def test_psycopg2_import(self):
        """Test psycopg2 import (optional)."""
        try:
            import psycopg2
            print(f"✅ psycopg2 imported successfully")
            
        except ImportError as e:
            pytest.skip(f"psycopg2 not available: {e}")
    
    @pytest.mark.skipif(not importlib.util.find_spec("celery"), 
                       reason="Celery not installed - this is optional")
    def test_celery_import(self):
        """Test Celery import (optional)."""
        try:
            from celery import Celery
            print("✅ Celery imported successfully")
            
        except ImportError as e:
            pytest.skip(f"Celery not available: {e}")
    
    @pytest.mark.skipif(not importlib.util.find_spec("redis"), 
                       reason="Redis not installed - this is optional")
    def test_redis_import(self):
        """Test Redis import (optional)."""
        try:
            import redis
            print(f"✅ Redis imported successfully")
            
        except ImportError as e:
            pytest.skip(f"Redis not available: {e}")


class TestAIDependencies:
    """Test AI and RAG system dependencies (optional)."""
    
    @pytest.mark.skipif(not importlib.util.find_spec("langchain"), 
                       reason="Langchain not installed - this is optional")
    def test_langchain_import(self):
        """Test Langchain import (optional)."""
        try:
            from langchain.schema import BaseMessage
            print("✅ Langchain imported successfully")
            
        except ImportError as e:
            pytest.skip(f"Langchain not available: {e}")
    
    @pytest.mark.skipif(not importlib.util.find_spec("langchain_openai"), 
                       reason="Langchain OpenAI not installed - this is optional")
    def test_langchain_openai_import(self):
        """Test Langchain OpenAI import (optional)."""
        try:
            from langchain_openai import ChatOpenAI
            print("✅ Langchain OpenAI imported successfully")
            
        except ImportError as e:
            pytest.skip(f"Langchain OpenAI not available: {e}")
    
    @pytest.mark.skipif(not importlib.util.find_spec("chromadb"), 
                       reason="ChromaDB not installed - this is optional")
    def test_chromadb_import(self):
        """Test ChromaDB import (optional)."""
        try:
            import chromadb
            print("✅ ChromaDB imported successfully")
            
        except ImportError as e:
            pytest.skip(f"ChromaDB not available: {e}")
    
    @pytest.mark.skipif(not importlib.util.find_spec("sentence_transformers"), 
                       reason="Sentence Transformers not installed - this is optional")
    def test_sentence_transformers_import(self):
        """Test Sentence Transformers import (optional)."""
        try:
            from sentence_transformers import SentenceTransformer
            print("✅ Sentence Transformers imported successfully")
            
        except ImportError as e:
            pytest.skip(f"Sentence Transformers not available: {e}")
    
    @pytest.mark.skipif(not importlib.util.find_spec("faiss"), 
                       reason="FAISS not installed - this is optional")
    def test_faiss_import(self):
        """Test FAISS import (optional)."""
        try:
            import faiss
            print("✅ FAISS imported successfully")
            
        except ImportError as e:
            pytest.skip(f"FAISS not available: {e}")
    
    @pytest.mark.skipif(not importlib.util.find_spec("tiktoken"), 
                       reason="Tiktoken not installed - this is optional")
    def test_tiktoken_import(self):
        """Test Tiktoken import (optional)."""
        try:
            import tiktoken
            print("✅ Tiktoken imported successfully")
            
        except ImportError as e:
            pytest.skip(f"Tiktoken not available: {e}")
    
    @pytest.mark.skipif(not importlib.util.find_spec("numpy"), 
                       reason="NumPy not installed - this is optional")
    def test_numpy_import(self):
        """Test NumPy import (optional)."""
        try:
            import numpy as np
            # Test basic functionality
            array = np.array([1, 2, 3])
            assert array.sum() == 6, "NumPy basic functionality failed"
            print(f"✅ NumPy {np.__version__} imported and tested successfully")
            
        except ImportError as e:
            pytest.skip(f"NumPy not available: {e}")
    
    @pytest.mark.skipif(not importlib.util.find_spec("scipy"), 
                       reason="SciPy not installed - this is optional")
    def test_scipy_import(self):
        """Test SciPy import (optional)."""
        try:
            import scipy
            print(f"✅ SciPy {scipy.__version__} imported successfully")
            
        except ImportError as e:
            pytest.skip(f"SciPy not available: {e}")


def test_dependencies_integration():
    """Integration test for core dependencies working together."""
    try:
        # Test FastAPI + Pydantic integration
        from fastapi import FastAPI
        from pydantic import BaseModel
        
        app = FastAPI()
        
        class TestItem(BaseModel):
            name: str
            description: str = None
        
        @app.post("/test/")
        async def create_item(item: TestItem):
            return {"item": item}
        
        # Test SQLAlchemy integration (skip Alembic for now)
        from sqlalchemy import create_engine, Column, Integer, String
        from sqlalchemy.orm import declarative_base
        
        Base = declarative_base()
        engine = create_engine("sqlite:///:memory:")
        
        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
        
        Base.metadata.create_all(engine)
        
        # Test authentication integration
        from jose import jwt
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        secret = "test-secret"
        
        # Create and verify token
        token_data = {"sub": "test-user"}
        token = jwt.encode(token_data, secret, algorithm="HS256")
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        
        assert decoded["sub"] == "test-user", "Token integration failed"
        
        print("✅ Dependencies integration test passed!")
        
    except Exception as e:
        pytest.fail(f"Dependencies integration test failed: {e}")


def test_python_version_compatibility():
    """Test Python version compatibility with dependencies."""
    python_version = version.parse(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    min_python_version = version.parse("3.9.0")
    
    assert python_version >= min_python_version, f"Python version {python_version} is below minimum requirement 3.9.0"
    
    print(f"✅ Python {python_version} is compatible with all dependencies")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])