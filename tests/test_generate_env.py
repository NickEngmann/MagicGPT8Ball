import os
import sys
import tempfile
import shutil
from unittest.mock import MagicMock
import pytest

# Extract core logic from generate_env.py (PlatformIO env-independent)
def generate_env_file_logic(project_dir, env_example_content=None, env_content=None):
    """
    Extracted logic from generate_env.py:
    - Creates data directory
    - Copies .env if exists, else .env.example, else exits
    Returns: (success, message)
    """
    # Ensure data directory exists
    data_dir = os.path.join(project_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Path to env files
    env_example = os.path.join(project_dir, '.env.example')
    env_file = os.path.join(project_dir, '.env')
    env_data = os.path.join(data_dir, '.env')
    
    # If .env exists, copy it to data directory
    if os.path.exists(env_file):
        shutil.copy2(env_file, env_data)
        return True, "Copied .env to data directory"
    # If not, copy example file
    elif os.path.exists(env_example):
        shutil.copy2(env_example, env_data)
        return True, "Warning: Using .env.example! Create .env file for production."
    else:
        return False, "Error: Neither .env nor .env.example found!"

class TestGenerateEnvLogic:
    """Test extracted logic from generate_env.py without PlatformIO dependencies"""

    def test_copies_existing_env_file(self):
        """Test copying existing .env to data/.env"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .env file
            env_file = os.path.join(tmpdir, '.env')
            with open(env_file, 'w') as f:
                f.write("API_KEY=secret123\n")
            
            success, message = generate_env_file_logic(tmpdir)
            
            assert success is True
            assert "Copied .env to data directory" in message
            assert os.path.exists(os.path.join(tmpdir, 'data', '.env'))
            with open(os.path.join(tmpdir, 'data', '.env')) as f:
                assert "API_KEY=secret123" in f.read()

    def test_copies_env_example_when_no_env(self):
        """Test copying .env.example when .env doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .env.example file
            env_example = os.path.join(tmpdir, '.env.example')
            with open(env_example, 'w') as f:
                f.write("API_KEY=default\n")
            
            success, message = generate_env_file_logic(tmpdir)
            
            assert success is True
            assert "Warning: Using .env.example" in message
            assert os.path.exists(os.path.join(tmpdir, 'data', '.env'))
            with open(os.path.join(tmpdir, 'data', '.env')) as f:
                assert "API_KEY=default" in f.read()

    def test_fails_when_no_env_files(self):
        """Test failure when neither .env nor .env.example exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            success, message = generate_env_file_logic(tmpdir)
            
            assert success is False
            assert "Error: Neither .env nor .env.example found" in message
            assert not os.path.exists(os.path.join(tmpdir, 'data', '.env'))

    def test_creates_data_directory(self):
        """Test that data directory is created if missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = os.path.join(tmpdir, 'data')
            assert not os.path.exists(data_dir)
            
            # Create .env.example to trigger copy
            env_example = os.path.join(tmpdir, '.env.example')
            with open(env_example, 'w') as f:
                f.write("TEST=1\n")
            
            generate_env_file_logic(tmpdir)
            
            assert os.path.exists(data_dir)
            assert os.path.isdir(data_dir)

    def test_preserves_file_permissions(self):
        """Test that shutil.copy2 preserves metadata (permissions)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = os.path.join(tmpdir, '.env')
            with open(env_file, 'w') as f:
                f.write("SECRET=abc\n")
            # Set specific permissions (400 = read-only)
            os.chmod(env_file, 0o400)
            
            generate_env_file_logic(tmpdir)
            
            copied_file = os.path.join(tmpdir, 'data', '.env')
            assert os.path.exists(copied_file)
            # copy2 preserves metadata, so permissions should match
            assert oct(os.stat(copied_file).st_mode)[-3:] == oct(0o400)[-3:]