#!/usr/bin/env python3
"""Unit tests for generate_env.py - environment file generation logic."""

import os
import tempfile
import shutil
import unittest
from pathlib import Path

# Create a temporary directory for test files
test_dir = tempfile.mkdtemp()
data_dir = os.path.join(test_dir, 'data')
project_dir = test_dir

# Create .env.example file
env_example_path = os.path.join(project_dir, '.env.example')
with open(env_example_path, 'w') as f:
    f.write("WIFI_SSID=test_wifi\nWIFI_PASSWORD=test_pass\n")

# Create a fake env.py to simulate PlatformIO env object
class FakeEnv:
    def __init__(self, project_dir):
        self.project_dir = project_dir
    
    def get(self, key):
        if key == 'PROJECT_DIR':
            return self.project_dir
        return None
    
    def Exit(self, code):
        raise SystemExit(code)

def generate_env_file(env):
    """Extracted function from generate_env.py for testing."""
    # Ensure data directory exists
    data_dir = os.path.join(env.get('PROJECT_DIR'), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Path to env files
    env_example = os.path.join(env.get('PROJECT_DIR'), '.env.example')
    env_file = os.path.join(env.get('PROJECT_DIR'), '.env')
    env_data = os.path.join(data_dir, '.env')
    
    # If .env exists, copy it to data directory
    if os.path.exists(env_file):
        shutil.copy2(env_file, env_data)
        print("Copied .env to data directory")
    # If not, copy example file
    elif os.path.exists(env_example):
        shutil.copy2(env_example, env_data)
        print("Warning: Using .env.example! Create .env file for production.")
    else:
        print("Error: Neither .env nor .env.example found!")
        env.Exit(1)

class TestGenerateEnv(unittest.TestCase):
    """Test cases for environment file generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, 'data')
        self.env_example = os.path.join(self.test_dir, '.env.example')
        self.env_file = os.path.join(self.test_dir, '.env')
        self.env_data = os.path.join(self.data_dir, '.env')
        
        # Create .env.example with test content
        with open(self.env_example, 'w') as f:
            f.write("WIFI_SSID=test_wifi\nWIFI_PASSWORD=test_pass\n")
        
        # Create fake env object
        self.env = FakeEnv(self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_creates_data_directory(self):
        """Test that data directory is created."""
        generate_env_file(self.env)
        self.assertTrue(os.path.exists(self.data_dir))
        self.assertTrue(os.path.isdir(self.data_dir))
    
    def test_copies_from_example_when_no_env(self):
        """Test copying .env.example to data directory."""
        generate_env_file(self.env)
        self.assertTrue(os.path.exists(self.env_data))
        
        # Verify content
        with open(self.env_data, 'r') as f:
            content = f.read()
        self.assertIn("WIFI_SSID=test_wifi", content)
        self.assertIn("WIFI_PASSWORD=test_pass", content)
    
    def test_copies_real_env_when_exists(self):
        """Test that real .env is preferred over .env.example."""
        # Create a real .env file
        with open(self.env_file, 'w') as f:
            f.write("WIFI_SSID=real_wifi\nWIFI_PASSWORD=real_pass\n")
        
        generate_env_file(self.env)
        self.assertTrue(os.path.exists(self.env_data))
        
        # Verify it copied the real .env, not the example
        with open(self.env_data, 'r') as f:
            content = f.read()
        self.assertIn("WIFI_SSID=real_wifi", content)
        self.assertIn("WIFI_PASSWORD=real_pass", content)
        self.assertNotIn("test_wifi", content)
    
    def test_exits_when_no_env_files_exist(self):
        """Test that function exits when neither .env nor .env.example exist."""
        # Remove .env.example
        os.remove(self.env_example)
        
        # Should raise SystemExit
        with self.assertRaises(SystemExit):
            generate_env_file(self.env)
        
        # Data directory should not be created
        self.assertFalse(os.path.exists(self.env_data))


if __name__ == '__main__':
    unittest.main()
