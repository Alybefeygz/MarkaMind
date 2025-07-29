"""
Backend project structure validation tests.
Tests all required folders and __init__.py files exist for FastAPI backend.
"""

import os
import pytest
from pathlib import Path


class TestProjectStructure:
    """Test class for validating backend project directory structure."""
    
    @pytest.fixture(scope="class")
    def project_root(self):
        """Get project root directory."""
        return Path(__file__).parent.parent
    
    def test_main_directories_exist(self, project_root):
        """Test that all main directories exist."""
        required_dirs = [
            "app",
            "tests", 
            "alembic",
            "scripts"
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Directory '{dir_name}' does not exist"
            assert dir_path.is_dir(), f"'{dir_name}' is not a directory"
    
    def test_app_subdirectories_exist(self, project_root):
        """Test that all app subdirectories exist."""
        app_subdirs = [
            "app/config",
            "app/core", 
            "app/models",
            "app/schemas",
            "app/api",
            "app/api/v1",
            "app/api/v1/endpoints",
            "app/services",
            "app/repositories",
            "app/integrations",
            "app/integrations/supabase",
            "app/integrations/openrouter",
            "app/tasks"
        ]
        
        for subdir in app_subdirs:
            dir_path = project_root / subdir
            assert dir_path.exists(), f"App subdirectory '{subdir}' does not exist"
            assert dir_path.is_dir(), f"'{subdir}' is not a directory"
    
    def test_test_subdirectories_exist(self, project_root):
        """Test that all test subdirectories exist."""
        test_subdirs = [
            "tests/test_api",
            "tests/test_services", 
            "tests/test_models",
            "tests/test_integrations"
        ]
        
        for subdir in test_subdirs:
            dir_path = project_root / subdir
            assert dir_path.exists(), f"Test subdirectory '{subdir}' does not exist"
            assert dir_path.is_dir(), f"'{subdir}' is not a directory"
    
    def test_required_python_files_exist(self, project_root):
        """Test that all required Python files exist."""
        required_files = [
            # Main app files
            "app/__init__.py",
            "app/main.py",
            
            # Config files
            "app/config/__init__.py",
            "app/config/settings.py",
            "app/config/database.py", 
            "app/config/logging.py",
            
            # Core files
            "app/core/__init__.py",
            "app/core/security.py",
            "app/core/dependencies.py",
            "app/core/exceptions.py",
            
            # Models
            "app/models/__init__.py",
            "app/models/base.py",
            "app/models/user.py",
            "app/models/chatbot.py",
            "app/models/conversation.py",
            
            # Schemas
            "app/schemas/__init__.py", 
            "app/schemas/user.py",
            "app/schemas/chatbot.py",
            
            # API
            "app/api/__init__.py",
            "app/api/deps.py",
            "app/api/v1/__init__.py",
            "app/api/v1/router.py",
            "app/api/v1/endpoints/__init__.py",
            "app/api/v1/endpoints/auth.py",
            "app/api/v1/endpoints/chatbots.py", 
            "app/api/v1/endpoints/training.py",
            "app/api/v1/endpoints/chat.py",
            
            # Services
            "app/services/__init__.py",
            "app/services/auth_service.py",
            "app/services/chatbot_service.py",
            "app/services/rag_service.py",
            "app/services/ai_service.py",
            
            # Repositories
            "app/repositories/__init__.py",
            "app/repositories/base.py",
            "app/repositories/user_repository.py",
            "app/repositories/chatbot_repository.py",
            
            # Integrations
            "app/integrations/__init__.py",
            "app/integrations/supabase/__init__.py",
            "app/integrations/supabase/client.py",
            "app/integrations/openrouter/__init__.py", 
            "app/integrations/openrouter/client.py",
            
            # Tasks
            "app/tasks/__init__.py",
            "app/tasks/celery_app.py",
            "app/tasks/training_tasks.py",
            
            # Tests
            "tests/__init__.py",
            "tests/conftest.py",
            "tests/test_api/__init__.py",
            "tests/test_services/__init__.py",
            "tests/test_models/__init__.py", 
            "tests/test_integrations/__init__.py",
            
            # Alembic
            "alembic/env.py",
            
            # Scripts
            "scripts/create-superuser.py"
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Required file '{file_path}' does not exist"
            assert full_path.is_file(), f"'{file_path}' is not a file"
    
    def test_required_config_files_exist(self, project_root):
        """Test that all required configuration files exist."""
        config_files = [
            "requirements.txt",
            "requirements-dev.txt", 
            ".env.example",
            "Dockerfile",
            "docker-compose.yml",
            "README.md",
            "alembic/alembic.ini"
        ]
        
        for file_path in config_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Configuration file '{file_path}' does not exist"
            assert full_path.is_file(), f"'{file_path}' is not a file"
    
    def test_init_files_in_python_packages(self, project_root):
        """Test that all Python package directories have __init__.py files."""
        python_packages = [
            "app",
            "app/config",
            "app/core",
            "app/models", 
            "app/schemas",
            "app/api",
            "app/api/v1",
            "app/api/v1/endpoints",
            "app/services",
            "app/repositories",
            "app/integrations",
            "app/integrations/supabase",
            "app/integrations/openrouter",
            "app/tasks",
            "tests",
            "tests/test_api",
            "tests/test_services",
            "tests/test_models",
            "tests/test_integrations"
        ]
        
        for package_dir in python_packages:
            init_file = project_root / package_dir / "__init__.py"
            assert init_file.exists(), f"Package '{package_dir}' missing __init__.py file"
            assert init_file.is_file(), f"__init__.py in '{package_dir}' is not a file"
    
    def test_backend_specific_structure(self, project_root):
        """Test backend-specific directory structure (no frontend dirs)."""
        # Ensure no frontend directories exist
        frontend_dirs = [
            "frontend",
            "client", 
            "web",
            "static",
            "templates",
            "public",
            "src"
        ]
        
        for frontend_dir in frontend_dirs:
            dir_path = project_root / frontend_dir
            assert not dir_path.exists(), f"Frontend directory '{frontend_dir}' should not exist in backend-only project"
    
    def test_fastapi_specific_structure(self, project_root):
        """Test FastAPI-specific structure requirements."""
        # Check for FastAPI-specific patterns
        api_structure_requirements = [
            ("app/main.py", "FastAPI main application file"),
            ("app/api/v1/router.py", "API v1 router file"),
            ("app/api/v1/endpoints", "API endpoints directory"),
            ("app/core/dependencies.py", "FastAPI dependencies file"),
            ("app/schemas", "Pydantic schemas directory")
        ]
        
        for file_or_dir, description in api_structure_requirements:
            path = project_root / file_or_dir
            assert path.exists(), f"{description} does not exist at '{file_or_dir}'"
    
    def test_clean_architecture_structure(self, project_root):
        """Test Clean Architecture pattern compliance."""
        # Verify separation of concerns
        architecture_layers = [
            ("app/models", "Data models layer"),
            ("app/schemas", "Data transfer objects layer"), 
            ("app/repositories", "Data access layer"),
            ("app/services", "Business logic layer"),
            ("app/api", "Presentation layer")
        ]
        
        for layer_dir, description in architecture_layers:
            path = project_root / layer_dir
            assert path.exists(), f"{description} directory does not exist at '{layer_dir}'"
            assert path.is_dir(), f"{description} path is not a directory"
    
    def test_integration_structure(self, project_root):
        """Test external integration structure."""
        integration_dirs = [
            "app/integrations/supabase",
            "app/integrations/openrouter"
        ]
        
        for integration_dir in integration_dirs:
            dir_path = project_root / integration_dir
            assert dir_path.exists(), f"Integration directory '{integration_dir}' does not exist"
            
            # Check for client.py in each integration
            client_file = dir_path / "client.py"
            assert client_file.exists(), f"Client file missing in '{integration_dir}'"
    
    def test_background_tasks_structure(self, project_root):
        """Test background tasks (Celery) structure."""
        tasks_dir = project_root / "app/tasks"
        assert tasks_dir.exists(), "Tasks directory does not exist"
        
        required_task_files = [
            "celery_app.py",
            "training_tasks.py"
        ]
        
        for task_file in required_task_files:
            file_path = tasks_dir / task_file
            assert file_path.exists(), f"Task file '{task_file}' does not exist"
    
    def test_database_migration_structure(self, project_root):
        """Test Alembic migration structure."""
        alembic_dir = project_root / "alembic"
        assert alembic_dir.exists(), "Alembic directory does not exist"
        
        versions_dir = alembic_dir / "versions"
        assert versions_dir.exists(), "Alembic versions directory does not exist"
        
        required_alembic_files = [
            "env.py",
            "alembic.ini"
        ]
        
        for alembic_file in required_alembic_files:
            if alembic_file == "alembic.ini":
                file_path = alembic_dir / alembic_file 
            else:
                file_path = alembic_dir / alembic_file
            assert file_path.exists(), f"Alembic file '{alembic_file}' does not exist"


def test_project_structure_complete():
    """Integration test to verify complete project structure."""
    project_root = Path(__file__).parent.parent
    
    # Count total directories and files created
    all_dirs = list(project_root.rglob("*/"))
    all_files = list(project_root.rglob("*"))
    all_files = [f for f in all_files if f.is_file()]
    
    print(f"Total directories created: {len(all_dirs)}")
    print(f"Total files created: {len(all_files)}")
    
    # Ensure minimum structure requirements are met
    assert len(all_dirs) >= 15, "Not enough directories created"
    assert len(all_files) >= 50, "Not enough files created"
    
    print("✅ Backend project structure validation complete!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])