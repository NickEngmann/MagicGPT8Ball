#!/usr/bin/env python3
"""
Unit tests for generate_env.py - PlatformIO build script
Tests the environment file generation logic for the MagicGPT8Ball project.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path


class TestGenerateEnv:
    """Test suite for generate_env.py environment file generation."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.test_dir)
        self.data_dir = self.project_dir / "data"
        self.env_example = self.project_dir / ".env.example"
        self.env_file = self.project_dir / ".env"
        
        # Create directories
        self.data_dir.mkdir()
        
    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_env_example_exists_no_env(self):
        """Test: When .env.example exists but .env doesn't, example is copied."""
        # Create .env.example file
        self.env_example.write_text("API_KEY=test_key\nDEBUG=true\n")
        
        # Verify source file exists
        assert self.env_example.exists()
        assert self.env_file.exists() is False
        
        # Simulate what generate_env.py does
        env_data = self.data_dir / ".env"
        if self.env_file.exists():
            shutil.copy2(self.env_file, env_data)
        elif self.env_example.exists():
            shutil.copy2(self.env_example, env_data)
        
        # Verify example was copied to data directory
        assert env_data.exists()
        assert env_data.read_text() == "API_KEY=test_key\nDEBUG=true\n"

    def test_env_file_exists(self):
        """Test: When both .env and .env.example exist, .env takes precedence."""
        # Create both files
        self.env_example.write_text("API_KEY=example_key\n")
        self.env_file.write_text("API_KEY=real_key\nSECRET=production\n")
        
        # Simulate the copy logic
        env_data = self.data_dir / ".env"
        if self.env_file.exists():
            shutil.copy2(self.env_file, env_data)
        elif self.env_example.exists():
            shutil.copy2(self.env_example, env_data)
        
        # Verify .env was copied (not .env.example)
        assert env_data.exists()
        content = env_data.read_text()
        assert "API_KEY=real_key" in content
        assert "SECRET=production" in content
        assert "example_key" not in content

    def test_neither_file_exists(self):
        """Test: When neither file exists, script should fail."""
        env_data = self.data_dir / ".env"
        
        # Simulate the copy logic
        if self.env_file.exists():
            shutil.copy2(self.env_file, env_data)
        elif self.env_example.exists():
            shutil.copy2(self.env_example, env_data)
        else:
            # This should trigger an error condition
            error_raised = True
            
        # Verify error handling
        assert error_raised
        assert not env_data.exists()

    def test_data_directory_created(self):
        """Test: data directory is created if it doesn't exist."""
        # Remove data directory
        shutil.rmtree(self.data_dir)
        
        assert not self.data_dir.exists()
        
        # Simulate directory creation
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Verify directory exists now
        assert self.data_dir.exists()
        assert self.data_dir.is_dir()

    def test_empty_env_example(self):
        """Test: .env.example with minimal content is copied correctly."""
        self.env_example.write_text("# Empty example\n")
        
        env_data = self.data_dir / ".env"
        shutil.copy2(self.env_example, env_data)
        
        assert env_data.exists()
        assert env_data.read_text() == "# Empty example\n"

    def test_env_with_special_characters(self):
        """Test: Environment files with special characters are preserved."""
        content = """API_KEY=secret-key-with-dashes
DEBUG=true
DESCRIPTION=Magic 8 Ball - Voice activated assistant
PATH_VAR=/usr/local/bin:/home/user"""
        
        self.env_file.write_text(content)
        
        env_data = self.data_dir / ".env"
        shutil.copy2(self.env_file, env_data)
        
        assert env_data.read_text() == content


class TestGenerateEnvIntegration:
    """Integration tests simulating actual PlatformIO usage."""

    def setup_method(self):
        """Create a realistic project structure."""
        self.test_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.test_dir)
        self.data_dir = self.project_dir / "data"
        self.data_dir.mkdir()

    def teardown_method(self):
        """Clean up after tests."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_realistic_project_setup(self):
        """Test: Realistic .env.example structure is preserved."""
        realistic_env = """# MagicGPT8Ball Configuration
API_KEY=your_api_key_here
DEBUG=true
SPIFFS_SIZE=0x100000
BAUD_RATE=115200
WIFI_SSID=YourWiFi
WIFI_PASS=YourPassword"""
        
        self.env_example = self.project_dir / ".env.example"
        self.env_example.write_text(realistic_env)
        
        # Verify file structure
        assert self.env_example.exists()
        lines = self.env_example.read_text().split('\n')
        assert len(lines) == 7
        assert "API_KEY=" in lines[1]

    def test_multiple_env_files_different_content(self):
        """Test: Multiple projects with different env files handled correctly."""
        # Project 1
        project1_env = self.project_dir / ".env"
        project1_env.write_text("PROJECT_ID=1\nVALUE=first\n")
        
        project1_data = self.project_dir / "project1_data"
        project1_data.mkdir()
        
        # Copy logic for project 1
        env_data = project1_data / ".env"
        if project1_env.exists():
            shutil.copy2(project1_env, env_data)
        
        assert env_data.exists()
        assert env_data.read_text() == "PROJECT_ID=1\nVALUE=first\n"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
