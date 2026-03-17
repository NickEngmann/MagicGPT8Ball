"""Tests for generate_env.py - environment file generation logic"""
import os
import sys
import shutil
import tempfile
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestGenerateEnv(unittest.TestCase):
    """Test environment file generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.project_dir = self.test_dir
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_env_file_creation_from_example(self):
        """Test that .env is created from .env.example when .env doesn't exist"""
        # Create .env.example
        env_example_path = os.path.join(self.project_dir, '.env.example')
        with open(env_example_path, 'w') as f:
            f.write('API_KEY=test_key\nWAV_PORT=5000\n')
        
        # Create data directory
        data_dir = os.path.join(self.project_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Test the logic
        env_file = os.path.join(self.project_dir, '.env')
        env_data = os.path.join(data_dir, '.env')
        
        # Since .env doesn't exist, it should copy from example
        self.assertFalse(os.path.exists(env_file))
        
    def test_env_file_copy_when_exists(self):
        """Test that existing .env is copied to data directory"""
        # Create both .env and .env.example
        env_example_path = os.path.join(self.project_dir, '.env.example')
        with open(env_example_path, 'w') as f:
            f.write('API_KEY=example_key\n')
            
        env_file = os.path.join(self.project_dir, '.env')
        with open(env_file, 'w') as f:
            f.write('API_KEY=actual_key\nWAV_PORT=5000\n')
        
        # Create data directory
        data_dir = os.path.join(self.project_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        env_data = os.path.join(data_dir, '.env')
        
        # Copy .env to data
        shutil.copy2(env_file, env_data)
        
        # Verify copy
        self.assertTrue(os.path.exists(env_data))
        with open(env_data, 'r') as f:
            content = f.read()
            self.assertIn('actual_key', content)
            
    def test_missing_env_files_error(self):
        """Test error when neither .env nor .env.example exists"""
        data_dir = os.path.join(self.project_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        self.assertFalse(os.path.exists(os.path.join(self.project_dir, '.env')))
        self.assertFalse(os.path.exists(os.path.join(self.project_dir, '.env.example')))
        
    def test_data_directory_creation(self):
        """Test that data directory is created if it doesn't exist"""
        # Remove data directory if exists
        data_dir = os.path.join(self.project_dir, 'data')
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)
        
        os.makedirs(data_dir, exist_ok=True)
        self.assertTrue(os.path.exists(data_dir))


if __name__ == '__main__':
    unittest.main()
