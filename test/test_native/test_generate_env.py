#!/usr/bin/env python3
"""
Tests for generate_env.py logic - Environment file generation script
"""

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Import the generate_env logic directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class MockEnv:
    """Mock PlatformIO env object for testing"""
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.exit_called = False
        self.exit_code = 0
        self._data = {}
    
    def get(self, key):
        if key == 'PROJECT_DIR':
            return self.project_dir
        return self._data.get(key)
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def Exit(self, code=1):
        self.exit_called = True
        self.exit_code = code


def generate_env_file(env):
    """Execute the generate_env.py logic"""
    import shutil
    import os
    
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
    # If not, copy example file
    elif os.path.exists(env_example):
        shutil.copy2(env_example, env_data)
    else:
        env.Exit(1)


class TestGenerateEnv(unittest.TestCase):
    """Test cases for generate_env.py logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.env = MockEnv(self.test_dir)
        
        # Create .env.example file
        self.env_example_path = os.path.join(self.test_dir, ".env.example")
        with open(self.env_example_path, "w") as f:
            f.write("VALTOWN_URL=https://example.com\nDEVICE_TOKEN=abc123\n")
        
        # Create data directory
        os.makedirs(os.path.join(self.test_dir, "data"), exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_env_file_not_exists_uses_example(self):
        """Test that when .env doesn't exist, .env.example is copied"""
        generate_env_file(self.env)
        
        # Check that data directory was created
        data_dir = os.path.join(self.test_dir, "data")
        self.assertTrue(os.path.exists(data_dir))
        
        # Check that .env was copied to data directory
        env_data_path = os.path.join(data_dir, ".env")
        self.assertTrue(os.path.exists(env_data_path))
        
        # Check that .env contains content from example
        with open(env_data_path, "r") as f:
            content = f.read()
        self.assertIn("VALTOWN_URL=", content)
        self.assertIn("DEVICE_TOKEN=", content)
    
    def test_env_file_exists_copies_env(self):
        """Test that existing .env file is copied to data directory"""
        # Create .env file with different content
        env_file_path = os.path.join(self.test_dir, ".env")
        with open(env_file_path, "w") as f:
            f.write("VALTOWN_URL=https://real.example.com\nDEVICE_TOKEN=real_token\n")
        
        generate_env_file(self.env)
        
        # Check that .env was copied (not .env.example)
        env_data_path = os.path.join(self.test_dir, "data", ".env")
        self.assertTrue(os.path.exists(env_data_path))
        
        with open(env_data_path, "r") as f:
            content = f.read()
        self.assertIn("VALTOWN_URL=https://real.example.com", content)
        self.assertIn("DEVICE_TOKEN=real_token", content)
    
    def test_no_env_file_fails(self):
        """Test that missing both .env and .env.example causes error"""
        # Remove .env.example
        os.remove(self.env_example_path)
        
        # Create a new env for this test
        env_no_example = MockEnv(self.test_dir)
        generate_env_file(env_no_example)
        
        # Check that Exit was called
        self.assertTrue(env_no_example.exit_called)
        self.assertEqual(env_no_example.exit_code, 1)
        
        # Check that data directory still exists
        data_dir = os.path.join(self.test_dir, "data")
        self.assertTrue(os.path.exists(data_dir))
        
        # Check that no .env file was created
        env_data_path = os.path.join(data_dir, ".env")
        self.assertFalse(os.path.exists(env_data_path))


class TestGenerateEnvIntegration(unittest.TestCase):
    """Integration tests using the actual project directory"""
    
    def test_project_generate_env_with_example(self):
        """Test generate_env.py with actual .env.example in project"""
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        env = MockEnv(project_dir)
        
        # Check that .env.example exists
        env_example = os.path.join(project_dir, ".env.example")
        self.assertTrue(os.path.exists(env_example), 
                       ".env.example should exist in project root")
        
        # Run the generation
        generate_env_file(env)
        
        # Check data directory was created
        data_dir = os.path.join(project_dir, "data")
        self.assertTrue(os.path.exists(data_dir))
        
        # Check .env was created in data directory
        env_data = os.path.join(data_dir, ".env")
        self.assertTrue(os.path.exists(env_data))
        
        # Verify content
        with open(env_data, "r") as f:
            content = f.read()
        self.assertGreater(len(content), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
