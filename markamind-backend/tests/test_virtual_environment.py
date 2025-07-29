"""
Virtual environment validation tests.
Tests Python version (3.9+), venv activation, and pip functionality.
"""

import os
import sys
import subprocess
import pytest
from pathlib import Path
from packaging import version


class TestVirtualEnvironment:
    """Test class for validating virtual environment setup."""
    
    @pytest.fixture(scope="class")
    def project_root(self):
        """Get project root directory."""
        return Path(__file__).parent.parent
    
    @pytest.fixture(scope="class")
    def venv_path(self, project_root):
        """Get virtual environment path."""
        return project_root / "venv"
    
    def test_python_version_requirement(self):
        """Test that Python version is 3.9 or higher."""
        python_version = version.parse(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        required_version = version.parse("3.9.0")
        
        assert python_version >= required_version, f"Python version {python_version} is below minimum requirement 3.9.0"
        print(f"✅ Python version {python_version} meets requirement (3.9+)")
    
    def test_virtual_environment_exists(self, venv_path):
        """Test that virtual environment directory exists."""
        assert venv_path.exists(), "Virtual environment directory 'venv' does not exist"
        assert venv_path.is_dir(), "Virtual environment path is not a directory"
        print(f"✅ Virtual environment directory exists at: {venv_path}")
    
    def test_virtual_environment_structure(self, venv_path):
        """Test that virtual environment has correct structure."""
        required_dirs = ["Scripts", "Lib", "Include"]
        required_files = ["pyvenv.cfg"]
        
        # Check directories
        for dir_name in required_dirs:
            dir_path = venv_path / dir_name
            assert dir_path.exists(), f"Virtual environment missing directory: {dir_name}"
            assert dir_path.is_dir(), f"Virtual environment {dir_name} is not a directory"
        
        # Check files
        for file_name in required_files:
            file_path = venv_path / file_name
            assert file_path.exists(), f"Virtual environment missing file: {file_name}"
            assert file_path.is_file(), f"Virtual environment {file_name} is not a file"
        
        print("✅ Virtual environment structure is correct")
    
    def test_python_executable_exists(self, venv_path):
        """Test that Python executable exists in virtual environment."""
        python_exe = venv_path / "Scripts" / "python.exe"
        assert python_exe.exists(), "Python executable not found in virtual environment"
        assert python_exe.is_file(), "Python executable path is not a file"
        print(f"✅ Python executable found: {python_exe}")
    
    def test_pip_executable_exists(self, venv_path):
        """Test that pip executable exists in virtual environment."""
        pip_exe = venv_path / "Scripts" / "pip.exe"
        assert pip_exe.exists(), "Pip executable not found in virtual environment"
        assert pip_exe.is_file(), "Pip executable path is not a file"
        print(f"✅ Pip executable found: {pip_exe}")
    
    def test_activation_scripts_exist(self, venv_path):
        """Test that activation scripts exist."""
        activation_scripts = [
            "Scripts/activate.bat",
            "Scripts/activate.ps1", 
            "Scripts/activate"
        ]
        
        for script in activation_scripts:
            script_path = venv_path / script
            assert script_path.exists(), f"Activation script not found: {script}"
            print(f"✅ Activation script found: {script}")
    
    def test_python_version_in_venv(self, venv_path):
        """Test Python version within virtual environment."""
        python_exe = venv_path / "Scripts" / "python.exe"
        
        try:
            result = subprocess.run(
                [str(python_exe), "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            
            version_output = result.stdout.strip()
            assert "Python" in version_output, "Invalid Python version output"
            
            # Extract version number
            version_str = version_output.split()[-1]
            python_version = version.parse(version_str)
            required_version = version.parse("3.9.0")
            
            assert python_version >= required_version, f"Virtual environment Python version {python_version} is below requirement 3.9.0"
            print(f"✅ Virtual environment Python version: {python_version}")
            
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to execute Python in virtual environment: {e}")
    
    def test_pip_version_in_venv(self, venv_path):
        """Test pip version within virtual environment."""
        pip_exe = venv_path / "Scripts" / "pip.exe"
        
        try:
            result = subprocess.run(
                [str(pip_exe), "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            
            version_output = result.stdout.strip()
            assert "pip" in version_output.lower(), "Invalid pip version output"
            
            # Normalize paths for comparison (handle both forward and backward slashes)
            venv_path_normalized = str(venv_path).replace("\\", "/")
            version_output_normalized = version_output.replace("\\", "/")
            assert venv_path_normalized in version_output_normalized, f"Pip is not using virtual environment. Expected path: {venv_path_normalized}, Got: {version_output_normalized}"
            
            print(f"✅ Virtual environment pip version: {version_output}")
            
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to execute pip in virtual environment: {e}")
    
    def test_pip_functionality(self, venv_path):
        """Test pip basic functionality (list installed packages)."""
        pip_exe = venv_path / "Scripts" / "pip.exe"
        
        try:
            result = subprocess.run(
                [str(pip_exe), "list"],
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout.strip()
            assert "pip" in output.lower(), "Pip package not found in pip list"
            assert "setuptools" in output.lower(), "Setuptools package not found in pip list"
            
            print("✅ Pip functionality test passed")
            print(f"Installed packages in virtual environment:\n{output}")
            
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to list packages with pip: {e}")
    
    def test_virtual_environment_isolation(self, venv_path):
        """Test that virtual environment is isolated from system Python."""
        python_exe = venv_path / "Scripts" / "python.exe"
        
        try:
            # Get Python path from virtual environment
            result = subprocess.run(
                [str(python_exe), "-c", "import sys; print(sys.executable)"],
                capture_output=True,
                text=True,
                check=True
            )
            
            venv_python_path = result.stdout.strip()
            venv_python_path_normalized = Path(venv_python_path).resolve()
            expected_path = (venv_path / "Scripts" / "python.exe").resolve()
            
            assert venv_python_path_normalized == expected_path, f"Virtual environment not isolated. Expected: {expected_path}, Got: {venv_python_path_normalized}"
            
            print(f"✅ Virtual environment is properly isolated")
            print(f"Virtual environment Python path: {venv_python_path}")
            
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to check virtual environment isolation: {e}")
    
    def test_environment_activation_helper_scripts(self, project_root):
        """Test that activation helper scripts exist and are functional."""
        helper_scripts = [
            "activate_venv.bat",
            "activate_venv.sh"
        ]
        
        for script in helper_scripts:
            script_path = project_root / script
            assert script_path.exists(), f"Activation helper script not found: {script}"
            assert script_path.is_file(), f"Activation helper script is not a file: {script}"
            
            # Check script content
            content = script_path.read_text(encoding='utf-8')
            assert "venv" in content.lower(), f"Helper script {script} does not reference virtual environment"
            assert "activate" in content.lower(), f"Helper script {script} does not contain activation command"
            
            print(f"✅ Activation helper script found and validated: {script}")
    
    def test_pyvenv_cfg_content(self, venv_path):
        """Test pyvenv.cfg file content."""
        pyvenv_cfg = venv_path / "pyvenv.cfg"
        assert pyvenv_cfg.exists(), "pyvenv.cfg file not found"
        
        content = pyvenv_cfg.read_text(encoding='utf-8')
        
        # Check required configurations  
        required_configs = [
            "home =",
            "include-system-site-packages =",
            "version ="
        ]
        
        for config in required_configs:
            assert config in content, f"Required configuration '{config}' not found in pyvenv.cfg"
        
        # Check that system site packages are disabled by default
        assert "include-system-site-packages = false" in content, "Virtual environment should not include system site packages by default"
        
        print("✅ pyvenv.cfg file content is valid")
        print(f"pyvenv.cfg content:\n{content}")


def test_virtual_environment_complete_setup():
    """Integration test for complete virtual environment setup."""
    project_root = Path(__file__).parent.parent
    venv_path = project_root / "venv"
    
    # Comprehensive validation
    assert venv_path.exists(), "Virtual environment not created"
    
    python_exe = venv_path / "Scripts" / "python.exe"
    pip_exe = venv_path / "Scripts" / "pip.exe"
    
    assert python_exe.exists(), "Python executable missing"
    assert pip_exe.exists(), "Pip executable missing"
    
    # Test Python version
    try:
        result = subprocess.run(
            [str(python_exe), "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version_str = result.stdout.split()[-1]
        python_version = version.parse(version_str)
        assert python_version >= version.parse("3.9.0"), "Python version requirement not met"
    except subprocess.CalledProcessError:
        pytest.fail("Failed to check Python version in virtual environment")
    
    # Test pip functionality
    try:
        subprocess.run(
            [str(pip_exe), "list"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError:
        pytest.fail("Pip functionality test failed")
    
    print("✅ Virtual environment complete setup validation passed!")
    print(f"Virtual environment location: {venv_path}")
    print(f"Python executable: {python_exe}")
    print(f"Pip executable: {pip_exe}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])