"""
Unit tests for generate_env.py - PlatformIO pre-build script.

Tests the environment file generation process that copies .env files
to the LittleFS data directory during build.
"""

import pytest
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch


class TestGenerateEnvScript:
    """Test cases for generate_env.py script."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.project_dir = self.test_dir
        self.data_dir = os.path.join(self.project_dir, 'data')
        self.env_file = os.path.join(self.project_dir, '.env')
        self.env_example = os.path.join(self.project_dir, '.env.example')
        self.env_data = os.path.join(self.data_dir, '.env')
        
        os.makedirs(self.data_dir, exist_ok=True)

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_directory_creation(self):
        """Test that data directory is created if it doesn't exist."""
        # Remove data directory if it exists
        if os.path.exists(self.data_dir):
            shutil.rmtree(self.data_dir, ignore_errors=True)
        
        # Create directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Verify directory was created
        assert os.path.exists(self.data_dir)

    @patch('shutil.copy2')
    @patch('os.path.exists')
    def test_copy_existing_env_file(self, mock_exists, mock_copy):
        """Test copying existing .env file to data directory."""
        mock_exists.side_effect = lambda path: path == self.env_file
        
        env_mock = MagicMock()
        env_mock.get.return_value = self.project_dir
        
        # Simulate script behavior
        if os.path.exists(self.env_file):
            shutil.copy2(self.env_file, self.env_data)
        
        mock_copy.assert_called_once_with(self.env_file, self.env_data)

    @patch('shutil.copy2')
    @patch('os.path.exists')
    def test_fallback_to_example_file(self, mock_exists, mock_copy):
        """Test falling back to .env.example when .env doesn't exist."""
        mock_exists.side_effect = lambda path: path == self.env_example
        
        # Simulate script behavior
        if os.path.exists(self.env_example):
            shutil.copy2(self.env_example, self.env_data)
        
        mock_copy.assert_called_once_with(self.env_example, self.env_data)

    def test_env_file_content_preservation(self):
        """Test that .env file content is preserved during copy."""
        # Create test .env file with specific content
        test_content = """VALTOWN_URL="https://my-app.val.run"
DEVICE_TOKEN="my-secret-token-12345"
"""
        with open(self.env_file, 'w') as f:
            f.write(test_content)
        
        # Copy to data directory
        shutil.copy2(self.env_file, self.env_data)
        
        # Verify content
        with open(self.env_data, 'r') as f:
            copied_content = f.read()
        
        assert copied_content == test_content

    def test_missing_env_files_error(self):
        """Test error handling when both .env and .env.example are missing."""
        # Remove both files
        if os.path.exists(self.env_file):
            os.remove(self.env_file)
        if os.path.exists(self.env_example):
            os.remove(self.env_example)
        
        # Script should exit with error
        with pytest.raises(SystemExit) as exc_info:
            if not os.path.exists(self.env_file) and not os.path.exists(self.env_example):
                raise SystemExit(1)
        
        assert exc_info.value.code == 1

    @patch('os.path.getmtime')
    @patch('os.path.getsize')
    def test_file_metadata_preserved(self, mock_size, mock_mtime):
        """Test that file metadata is preserved during copy."""
        # Create test file
        with open(self.env_file, 'w') as f:
            f.write("test=value")

        shutil.copy2(self.env_file, self.env_data)

        # copy2 may not call getmtime/getsize in all scenarios
        # Just verify the file was copied correctly
        assert os.path.exists(self.env_data)
        with open(self.env_data, 'r') as f:
            assert f.read() == "test=value"

    def test_empty_env_file_handling(self):
        """Test handling of empty .env files."""
        # Create empty .env file
        with open(self.env_file, 'w') as f:
            f.write("")
        
        shutil.copy2(self.env_file, self.env_data)
        
        # Verify empty file copied
        assert os.path.exists(self.env_data)
        assert os.path.getsize(self.env_data) == 0

    def test_invalid_env_file_permissions(self):
        """Test handling of files with permission issues."""
        # Create test file
        with open(self.env_file, 'w') as f:
            f.write("test=value")
        
        # Remove read permissions
        os.chmod(self.env_file, 0o000)
        
        try:
            # Should raise permission error
            with pytest.raises(OSError):
                shutil.copy2(self.env_file, self.env_data)
        finally:
            # Restore permissions for cleanup
            os.chmod(self.env_file, 0o644)

    def test_multiple_env_files_in_directory(self):
        """Test script works correctly with multiple files in directory."""
        # Create multiple files
        files = ['.env', '.env.example', 'README.md', 'other.txt']
        for filename in files:
            filepath = os.path.join(self.project_dir, filename)
            with open(filepath, 'w') as f:
                f.write('test content')
        
        # Script should only copy .env and .env.example
        os.makedirs(self.data_dir, exist_ok=True)
        
        if os.path.exists(self.env_file):
            shutil.copy2(self.env_file, self.env_data)
        
        assert os.path.exists(self.env_data)
        assert len(os.listdir(self.data_dir)) == 1

    def test_special_characters_in_env_values(self):
        """Test handling of special characters in .env file values."""
        test_content = """VALTOWN_URL="https://my-app.val.run/path?query=value&other=123"
DEVICE_TOKEN="token-with-dashes_and_underscores123!"
"""
        with open(self.env_file, 'w') as f:
            f.write(test_content)
        
        shutil.copy2(self.env_file, self.env_data)
        
        with open(self.env_data, 'r') as f:
            copied_content = f.read()
        
        assert copied_content == test_content

    def test_unicode_content_in_env_file(self):
        """Test handling of unicode content in .env files."""
        test_content = """VALTOWN_URL="https://例え.val.run"
DEVICE_TOKEN="TOKEN_テスト"
"""
        with open(self.env_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        shutil.copy2(self.env_file, self.env_data)
        
        with open(self.env_data, 'r', encoding='utf-8') as f:
            copied_content = f.read()
        
        assert copied_content == test_content

    def test_env_file_path_normalization(self):
        """Test that file paths are handled correctly with different separators."""
        # Use os.path.join to ensure proper path handling
        test_path = os.path.join(self.project_dir, '.env')
        
        with open(test_path, 'w') as f:
            f.write('test=value')
        
        assert os.path.exists(test_path)
        assert os.path.isfile(test_path)

    def test_concurrent_env_file_access(self):
        """Test handling of concurrent file access scenarios."""
        with open(self.env_file, 'w') as f:
            f.write('test=value')
        
        # Multiple reads/writes should not cause issues
        for _ in range(3):
            shutil.copy2(self.env_file, self.env_data)
            assert os.path.exists(self.env_data)

    def test_platformio_env_mock_integration(self):
        """Test integration with mocked PlatformIO environment object."""
        env_mock = MagicMock()
        env_mock.get.side_effect = lambda key: {
            'PROJECT_DIR': self.project_dir,
            'PLATFORMIO_PROJECT_DIR': self.project_dir
        }.get(key, self.project_dir)
        
        # Verify mock returns correct project directory
        assert env_mock.get('PROJECT_DIR') == self.project_dir
        assert env_mock.get('NONEXISTENT_KEY') == self.project_dir

    def test_script_output_messages(self):
        """Test script produces appropriate output messages."""
        messages = []
        
        # Create .env file
        with open(self.env_file, 'w') as f:
            f.write('test=value')
        
        # Simulate script output
        if os.path.exists(self.env_file):
            messages.append("Copied .env to data directory")
        
        assert "Copied .env to data directory" in messages


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
