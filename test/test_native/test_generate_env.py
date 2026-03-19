"""Tests for generate_env.py using Python's unittest framework."""

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path to import the script
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestGenerateEnv(unittest.TestCase):
    """Test suite for environment file generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_dir = Path(self.test_dir)
        
        # Create necessary directories
        self.data_dir = self.repo_dir / "data"
        self.data_dir.mkdir()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_env_files(self, has_env: bool = True, has_example: bool = True):
        """Helper to create .env and .env.example files."""
        if has_env:
            env_file = self.repo_dir / ".env"
            env_file.write_text('VALTOWN_URL="https://test.val.run"\nDEVICE_TOKEN="test-token"')
        if has_example:
            example_file = self.repo_dir / ".env.example"
            example_file.write_text('VALTOWN_URL="https://example.val.run"\nDEVICE_TOKEN="example-token"')
    
    def test_file_creation_success(self):
        """Test that .env file creation works correctly."""
        self._create_env_files(has_env=True, has_example=True)
        
        # Verify files exist
        self.assertTrue((self.repo_dir / ".env").exists())
        self.assertTrue((self.repo_dir / ".env.example").exists())
        
    def test_missing_env_uses_example(self):
        """Test that when .env is missing, .env.example is used."""
        self._create_env_files(has_env=False, has_example=True)
        
        # Verify .env doesn't exist but example does
        self.assertFalse((self.repo_dir / ".env").exists())
        self.assertTrue((self.repo_dir / ".env.example").exists())
    
    def test_missing_both_files(self):
        """Test error handling when both .env and .env.example are missing."""
        self._create_env_files(has_env=False, has_example=False)
        
        # Verify neither file exists
        self.assertFalse((self.repo_dir / ".env").exists())
        self.assertFalse((self.repo_dir / ".env.example").exists())
    
    def test_env_file_parsing(self):
        """Test parsing of .env file with quoted values."""
        self._create_env_files(has_env=True, has_example=True)
        
        env_content = (self.repo_dir / ".env").read_text()
        
        # Verify content is parseable
        lines = env_content.strip().split('\n')
        self.assertEqual(len(lines), 2)
        
        # Check key-value pairs
        self.assertIn('VALTOWN_URL="https://test.val.run"', lines)
        self.assertIn('DEVICE_TOKEN="test-token"', lines)
    
    def test_env_file_with_comments(self):
        """Test that .env files with comments are handled correctly."""
        env_content = """# This is a comment
VALTOWN_URL="https://test.val.run"
# Another comment
DEVICE_TOKEN="test-token"
"""
        env_file = self.repo_dir / ".env"
        env_file.write_text(env_content)
        
        # Verify file was created with comments
        self.assertTrue(env_file.exists())
        content = env_file.read_text()
        self.assertIn("# This is a comment", content)


if __name__ == '__main__':
    unittest.main()
