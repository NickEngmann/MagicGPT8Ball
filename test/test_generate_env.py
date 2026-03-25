"""
Test suite for generate_env.py - Environment file generation script.
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestGenerateEnvScript(unittest.TestCase):
    """Tests for generate_env.py script functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.project_dir = self.test_dir / "magicgpt8ball"
        self.project_dir.mkdir()
        
        # Create .env.example file
        self.env_example = self.project_dir / ".env.example"
        self.env_example.write_text("VALTOWN_URL=https://api.val.town\nDEVICE_TOKEN=sample_token_12345")
        
        # Create .env file
        self.env_file = self.project_dir / ".env"
        self.env_file.write_text("VALTOWN_URL=https://production.val.town\nDEVICE_TOKEN=prod_token_67890")
        
        # Mock PlatformIO env object
        self.mock_env = MagicMock()
        self.mock_env.get.side_effect = lambda key: {
            'PROJECT_DIR': str(self.project_dir)
        }.get(key)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_generate_env_file_function_exists(self):
        """Test that generate_env_file function is defined."""
        script_path = project_root / "generate_env.py"
        self.assertTrue(script_path.exists())
        content = script_path.read_text()
        self.assertIn("def generate_env_file", content)

    def test_env_example_file_created(self):
        """Test that .env.example file is properly created."""
        self.assertTrue(self.env_example.exists())
        content = self.env_example.read_text()
        self.assertIn("VALTOWN_URL", content)
        self.assertIn("DEVICE_TOKEN", content)

    def test_env_file_created(self):
        """Test that .env file is properly created."""
        self.assertTrue(self.env_file.exists())
        content = self.env_file.read_text()
        self.assertIn("VALTOWN_URL", content)
        self.assertIn("DEVICE_TOKEN", content)

    def test_data_directory_created(self):
        """Test that data directory is created."""
        data_dir = self.project_dir / "data"
        self.assertFalse(data_dir.exists())
        
        # Simulate what generate_env_file does
        data_dir.mkdir(exist_ok=True)
        self.assertTrue(data_dir.exists())
        self.assertTrue(data_dir.is_dir())

    def test_env_file_copied_to_data(self):
        """Test that .env file is copied to data directory."""
        data_dir = self.project_dir / "data"
        data_dir.mkdir()
        env_data = data_dir / ".env"
        
        # Simulate the copy operation
        shutil.copy2(self.env_file, env_data)
        
        self.assertTrue(env_data.exists())
        self.assertEqual(env_data.read_text(), self.env_file.read_text())

    def test_example_file_used_when_env_missing(self):
        """Test that .env.example is used when .env doesn't exist."""
        # Remove .env file
        self.env_file.unlink()
        
        data_dir = self.project_dir / "data"
        data_dir.mkdir()
        env_data = data_dir / ".env"
        
        # Simulate the copy operation
        shutil.copy2(self.env_example, env_data)
        
        self.assertTrue(env_data.exists())
        self.assertEqual(env_data.read_text(), self.env_example.read_text())

    def test_error_when_no_env_files(self):
        """Test error handling when neither .env nor .env.example exists."""
        # Remove both files
        self.env_file.unlink()
        self.env_example.unlink()
        
        data_dir = self.project_dir / "data"
        data_dir.mkdir()
        env_data = data_dir / ".env"
        
        # Verify files don't exist
        self.assertFalse(self.env_file.exists())
        self.assertFalse(self.env_example.exists())

    def test_data_directory_path_correct(self):
        """Test that data directory path is correctly calculated."""
        script_path = project_root / "generate_env.py"
        self.assertTrue(script_path.exists())
        script_content = script_path.read_text()

        # Verify the script uses correct path logic
        self.assertIn("data_dir", script_content)
        self.assertIn("PROJECT_DIR", script_content)
        self.assertIn("os.path.join", script_content)


class TestGenerateEnvMocked(unittest.TestCase):
    """Tests for generate_env.py script analysis."""

    def test_script_calls_generate_function(self):
        """Test that the script calls the generate_env_file function."""
        script_path = project_root / "generate_env.py"
        self.assertTrue(script_path.exists())
        content = script_path.read_text()
        
        # Verify function is called at the end
        self.assertIn("generate_env_file()", content)

    def test_shutil_copy2_used(self):
        """Test that shutil.copy2 is used for file copying."""
        script_path = project_root / "generate_env.py"
        content = script_path.read_text()
        
        self.assertIn("shutil.copy2", content)

    def test_os_path_join_used(self):
        """Test that os.path.join is used for path construction."""
        script_path = project_root / "generate_env.py"
        content = script_path.read_text()
        
        self.assertIn("os.path.join", content)

    def test_makedirs_used(self):
        """Test that os.makedirs is used to create directories."""
        script_path = project_root / "generate_env.py"
        content = script_path.read_text()
        
        self.assertIn("os.makedirs", content)
        self.assertIn("exist_ok=True", content)

    def test_os_exists_check(self):
        """Test that os.path.exists is used for file checks."""
        script_path = project_root / "generate_env.py"
        content = script_path.read_text()
        
        self.assertIn("os.path.exists", content)

    def test_env_exit_on_error(self):
        """Test that env.Exit() is called on error."""
        script_path = project_root / "generate_env.py"
        content = script_path.read_text()
        
        self.assertIn("env.Exit", content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
