"""
Docker configuration validation tests.
Tests Dockerfile build, docker-compose validation, and service connectivity.
"""

import os
import yaml
import pytest
from pathlib import Path
import subprocess
import json


class TestDockerfiles:
    """Test Docker configuration files."""
    
    def test_dockerfile_exists(self):
        """Test that Dockerfile exists."""
        project_root = Path(__file__).parent.parent
        dockerfile_path = project_root / "Dockerfile"
        
        assert dockerfile_path.exists(), "Dockerfile does not exist"
        assert dockerfile_path.is_file(), "Dockerfile is not a file"
        
        print("✅ Dockerfile exists")
    
    def test_dockerfile_content(self):
        """Test Dockerfile content."""
        project_root = Path(__file__).parent.parent
        dockerfile_path = project_root / "Dockerfile"
        
        content = dockerfile_path.read_text()
        
        # Check for required instructions
        required_instructions = [
            "FROM python:3.11-slim",
            "WORKDIR /app",
            "COPY requirements.txt",
            "RUN pip install",
            "COPY . .",
            "EXPOSE 8000",
            "CMD"
        ]
        
        for instruction in required_instructions:
            assert instruction in content, f"Required instruction '{instruction}' not found in Dockerfile"
        
        # Check for security best practices
        security_checks = [
            "useradd",  # Non-root user
            "USER app",  # Switch to non-root user
            "HEALTHCHECK"  # Health check
        ]
        
        for check in security_checks:
            assert check in content, f"Security practice '{check}' not found in Dockerfile"
        
        print("✅ Dockerfile content is correct")
    
    def test_dockerignore_exists(self):
        """Test that .dockerignore exists."""
        project_root = Path(__file__).parent.parent
        dockerignore_path = project_root / ".dockerignore"
        
        assert dockerignore_path.exists(), ".dockerignore does not exist"
        assert dockerignore_path.is_file(), ".dockerignore is not a file"
        
        print("✅ .dockerignore exists")
    
    def test_dockerignore_content(self):
        """Test .dockerignore content."""
        project_root = Path(__file__).parent.parent
        dockerignore_path = project_root / ".dockerignore"
        
        content = dockerignore_path.read_text()
        
        # Check for important exclusions
        required_exclusions = [
            "__pycache__",
            "*.pyc",
            ".git",
            "venv/",
            ".env",
            "*.log",
            ".pytest_cache"
        ]
        
        for exclusion in required_exclusions:
            assert exclusion in content, f"Required exclusion '{exclusion}' not found in .dockerignore"
        
        print("✅ .dockerignore content is correct")


class TestDockerCompose:
    """Test Docker Compose configuration."""
    
    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists."""
        project_root = Path(__file__).parent.parent
        compose_path = project_root / "docker-compose.yml"
        
        assert compose_path.exists(), "docker-compose.yml does not exist"
        assert compose_path.is_file(), "docker-compose.yml is not a file"
        
        print("✅ docker-compose.yml exists")
    
    def test_docker_compose_valid_yaml(self):
        """Test that docker-compose.yml is valid YAML."""
        project_root = Path(__file__).parent.parent
        compose_path = project_root / "docker-compose.yml"
        
        try:
            with open(compose_path, 'r') as f:
                compose_config = yaml.safe_load(f)
            
            assert compose_config is not None, "docker-compose.yml is empty"
            assert 'services' in compose_config, "No services defined in docker-compose.yml"
            
            print("✅ docker-compose.yml is valid YAML")
            
        except yaml.YAMLError as e:
            pytest.fail(f"docker-compose.yml is not valid YAML: {e}")
    
    def test_docker_compose_services(self):
        """Test docker-compose services configuration."""
        project_root = Path(__file__).parent.parent
        compose_path = project_root / "docker-compose.yml"
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        services = compose_config.get('services', {})
        
        # Check for required services
        required_services = ['api', 'db', 'redis', 'celery']
        
        for service in required_services:
            assert service in services, f"Required service '{service}' not found"
        
        # Check API service configuration
        api_service = services.get('api', {})
        assert 'build' in api_service, "API service missing build configuration"
        assert 'ports' in api_service, "API service missing ports configuration"
        assert 'environment' in api_service, "API service missing environment configuration"
        assert 'depends_on' in api_service, "API service missing dependencies"
        
        # Check database service
        db_service = services.get('db', {})
        assert db_service.get('image') == 'postgres:15', "Database service not using PostgreSQL 15"
        assert 'environment' in db_service, "Database service missing environment configuration"
        
        # Check Redis service
        redis_service = services.get('redis', {})
        assert 'redis' in redis_service.get('image', ''), "Redis service not using Redis image"
        
        print("✅ docker-compose services are correctly configured")
    
    def test_docker_compose_environment_variables(self):
        """Test environment variables configuration."""
        project_root = Path(__file__).parent.parent
        compose_path = project_root / "docker-compose.yml"
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        api_env = compose_config['services']['api']['environment']
        
        # Check for required environment variables
        required_env_vars = [
            'DATABASE_URL',
            'REDIS_URL',
            'SECRET_KEY',
            'ENVIRONMENT'
        ]
        
        # Convert list format to dict for easier checking
        env_dict = {}
        for env_item in api_env:
            if '=' in env_item:
                key, value = env_item.split('=', 1)
                env_dict[key] = value
        
        for var in required_env_vars:
            assert any(var in env_item for env_item in api_env), f"Required environment variable '{var}' not found"
        
        print("✅ Environment variables are correctly configured")
    
    def test_docker_compose_volumes(self):
        """Test volumes configuration."""
        project_root = Path(__file__).parent.parent
        compose_path = project_root / "docker-compose.yml"
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        # Check for volumes section
        assert 'volumes' in compose_config, "No volumes section found"
        
        volumes = compose_config['volumes']
        required_volumes = ['postgres_data', 'redis_data']
        
        for volume in required_volumes:
            assert volume in volumes, f"Required volume '{volume}' not found"
        
        print("✅ Volumes are correctly configured")
    
    def test_docker_compose_override_exists(self):
        """Test that docker-compose.override.yml exists for development."""
        project_root = Path(__file__).parent.parent
        override_path = project_root / "docker-compose.override.yml"
        
        assert override_path.exists(), "docker-compose.override.yml does not exist"
        
        with open(override_path, 'r') as f:
            override_config = yaml.safe_load(f)
        
        assert 'services' in override_config, "Override file missing services"
        
        print("✅ docker-compose.override.yml exists and is valid")


class TestDockerScripts:
    """Test Docker-related scripts."""
    
    def test_init_db_script_exists(self):
        """Test that database initialization script exists."""
        project_root = Path(__file__).parent.parent
        init_script_path = project_root / "scripts" / "init-db.sql"
        
        assert init_script_path.exists(), "Database initialization script does not exist"
        assert init_script_path.is_file(), "init-db.sql is not a file"
        
        print("✅ Database initialization script exists")
    
    def test_init_db_script_content(self):
        """Test database initialization script content."""
        project_root = Path(__file__).parent.parent
        init_script_path = project_root / "scripts" / "init-db.sql"
        
        content = init_script_path.read_text()
        
        # Check for basic SQL structure
        sql_checks = [
            "CREATE EXTENSION",
            "CREATE TABLE",
            "uuid-ossp",
            "health_check"
        ]
        
        for check in sql_checks:
            assert check in content, f"SQL statement '{check}' not found in init script"
        
        print("✅ Database initialization script content is correct")


class TestDockerIntegration:
    """Test Docker integration and connectivity (requires Docker)."""
    
    def test_docker_available(self):
        """Test that Docker is available on the system."""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            assert result.returncode == 0, "Docker is not available"
            print(f"✅ Docker is available: {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker is not available on this system")
    
    def test_docker_compose_available(self):
        """Test that Docker Compose is available."""
        try:
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                # Try newer Docker Compose v2 syntax
                result = subprocess.run(['docker', 'compose', 'version'], 
                                      capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0, "Docker Compose is not available"
            print(f"✅ Docker Compose is available: {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker Compose is not available on this system")
    
    def test_docker_compose_config_validation(self):
        """Test docker-compose configuration validation."""
        project_root = Path(__file__).parent.parent
        
        try:
            # Change to project directory
            os.chdir(project_root)
            
            # Validate docker-compose configuration
            result = subprocess.run(['docker-compose', 'config'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                # Try Docker Compose v2
                result = subprocess.run(['docker', 'compose', 'config'], 
                                      capture_output=True, text=True, timeout=30)
            
            assert result.returncode == 0, f"Docker Compose config validation failed: {result.stderr}"
            
            # Parse the output to ensure it's valid
            try:
                yaml.safe_load(result.stdout)
                print("✅ Docker Compose configuration is valid")
            except yaml.YAMLError as e:
                pytest.fail(f"Docker Compose config produces invalid YAML: {e}")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker Compose validation requires Docker to be installed")
    
    @pytest.mark.slow
    def test_dockerfile_build_syntax(self):
        """Test that Dockerfile has valid syntax (requires Docker)."""
        project_root = Path(__file__).parent.parent
        
        try:
            os.chdir(project_root)
            
            # Test Dockerfile syntax without actually building
            result = subprocess.run([
                'docker', 'build', '--dry-run', '.'
            ], capture_output=True, text=True, timeout=60)
            
            # Docker build --dry-run is not available in all versions
            # So we'll just test that Docker can parse the Dockerfile
            result = subprocess.run([
                'docker', 'build', '--no-cache', '--target', 'nonexistent', '.'
            ], capture_output=True, text=True, timeout=60)
            
            # This should fail because target doesn't exist, but if it fails due to 
            # syntax errors, we'll catch that
            if "dockerfile parse error" in result.stderr.lower():
                pytest.fail(f"Dockerfile syntax error: {result.stderr}")
            
            print("✅ Dockerfile syntax appears to be valid")
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker build test requires Docker to be installed")


def test_docker_setup_complete():
    """Integration test for complete Docker setup."""
    project_root = Path(__file__).parent.parent
    
    # Check all required files exist
    required_files = [
        "Dockerfile",
        "docker-compose.yml", 
        "docker-compose.override.yml",
        ".dockerignore",
        "scripts/init-db.sql"
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"Required Docker file '{file_path}' does not exist"
    
    # Check docker-compose.yml has all required services
    compose_path = project_root / "docker-compose.yml"
    with open(compose_path, 'r') as f:
        compose_config = yaml.safe_load(f)
    
    services = compose_config.get('services', {})
    required_services = ['api', 'db', 'redis', 'celery']
    
    for service in required_services:
        assert service in services, f"Required service '{service}' missing from docker-compose.yml"
    
    print("✅ Complete Docker setup validation passed!")
    print(f"Docker files: {len(required_files)} files created")
    print(f"Services: {len(required_services)} services configured")
    print("Docker setup is ready for development and production!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])