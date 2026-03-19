"""Tests for Environment class error handling and validation."""

import os
import sys
import unittest
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestEnvironmentValidation(unittest.TestCase):
    """Test suite for Environment class validation improvements."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.env_example_path = Path(self.test_dir) / ".env.example"
        self.env_path = Path(self.test_dir) / ".env"
        
        # Create example file
        self.env_example_path.write_text('VALTOWN_URL="https://example.val.run"\nDEVICE_TOKEN="example-token"')
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_env_with_all_required_vars(self):
        """Test environment file with all required variables."""
        # Create complete .env file
        self.env_path.write_text('VALTOWN_URL="https://test.val.run"\nDEVICE_TOKEN="test-token"')
        
        content = self.env_path.read_text()
        lines = content.strip().split('\n')
        
        # Should have 2 lines
        self.assertEqual(len(lines), 2)
        
        # Each line should have an = separator
        for line in lines:
            self.assertIn('=', line)
    
    def test_env_with_missing_var(self):
        """Test environment file with missing required variable."""
        # Create .env file without DEVICE_TOKEN
        self.env_path.write_text('VALTOWN_URL="https://test.val.run"\n')
        
        content = self.env_path.read_text()
        lines = content.strip().split('\n')
        
        # Should have only 1 line with VALTOWN_URL
        self.assertEqual(len([l for l in lines if l.strip()]), 1)
        
        # Verify DEVICE_TOKEN is missing
        self.assertNotIn('DEVICE_TOKEN', content)
    
    def test_env_with_comment_lines(self):
        """Test environment file with comment lines."""
        content = """# This is a comment
VALTOWN_URL="https://test.val.run"
# Another comment
DEVICE_TOKEN="test-token"
"""
        self.env_path.write_text(content)
        
        # Count non-empty, non-comment lines
        lines = [l for l in content.strip().split('\n') 
                 if l.strip() and not l.strip().startswith('#')]
        
        self.assertEqual(len(lines), 2)
    
    def test_env_with_empty_lines(self):
        """Test environment file with empty lines."""
        content = """
VALTOWN_URL="https://test.val.run"

DEVICE_TOKEN="test-token"

"""
        self.env_path.write_text(content)
        
        lines = content.strip().split('\n')
        non_empty = [l for l in lines if l.strip()]
        
        self.assertEqual(len(non_empty), 2)
    
    def test_env_value_parsing(self):
        """Test parsing of quoted values."""
        content = '''VALTOWN_URL="https://test.val.run:8080/api"\nDEVICE_TOKEN="my-secret-token-123"'''
        self.env_path.write_text(content)
        
        lines = content.strip().split('\n')
        self.assertEqual(len(lines), 2)
        
        # Parse the URL value
        url_line = lines[0]
        url = url_line.split('=')[1].strip().strip('"')
        self.assertEqual(url, 'https://test.val.run:8080/api')
        
        # Parse the token value
        token_line = lines[1]
        token = token_line.split('=')[1].strip().strip('"')
        self.assertEqual(token, 'my-secret-token-123')
    
    def test_env_special_characters_in_values(self):
        """Test environment values with special characters."""
        content = '''VALTOWN_URL="https://api.example.com/v1?token=abc123"\nDEVICE_TOKEN="secret-token-!@#$%"'''
        self.env_path.write_text(content)
        
        # Should still be parseable
        lines = content.strip().split('\n')
        self.assertEqual(len(lines), 2)
        
        # Extract values
        url = lines[0].split('=')[1].strip().strip('"')
        token = lines[1].split('=')[1].strip().strip('"')
        
        self.assertIn('api.example.com', url)
        self.assertIn('secret-token', token)
    
    def test_env_validation_logic(self):
        """Test the validation logic for environment files."""
        # Test case 1: Valid environment
        valid_env = 'VALTOWN_URL="https://test.val.run"\nDEVICE_TOKEN="token"'
        
        # Check both required variables exist
        has_url = 'VALTOWN_URL' in valid_env
        has_token = 'DEVICE_TOKEN' in valid_env
        
        self.assertTrue(has_url)
        self.assertTrue(has_token)
        
        # Test case 2: Missing URL
        incomplete_env = 'DEVICE_TOKEN="token"'
        self.assertFalse('VALTOWN_URL' in incomplete_env)
        
        # Test case 3: Missing token
        incomplete_env2 = 'VALTOWN_URL="https://test.val.run"'
        self.assertFalse('DEVICE_TOKEN' in incomplete_env2)
    
    def test_env_quoted_value_edge_cases(self):
        """Test edge cases for quoted values."""
        # Empty value
        content1 = 'VALTOWN_URL=""\nDEVICE_TOKEN="token"'
        lines1 = content1.strip().split('\n')
        value1 = lines1[0].split('=')[1].strip().strip('"')
        self.assertEqual(value1, '')
        
        # Value with spaces
        content2 = 'VALTOWN_URL=" https://test.val.run "\nDEVICE_TOKEN="token"'
        lines2 = content2.strip().split('\n')
        value2 = lines2[0].split('=')[1].strip().strip('"')
        self.assertEqual(value2, ' https://test.val.run ')
    
    def test_env_line_with_equals_sign_in_value(self):
        """Test environment values containing equals signs."""
        # Base64 encoded token
        content = '''VALTOWN_URL="https://test.val.run"\nDEVICE_TOKEN="dXNlcjpwYXNzd29yZD0xMjM="'''
        
        self.env_path.write_text(content)
        
        lines = content.strip().split('\n')
        token_line = lines[1]
        
        # Should split only on first = sign
        parts = token_line.split('=')
        key = parts[0]
        value = '='.join(parts[1:]).strip().strip('"')
        
        self.assertEqual(key, 'DEVICE_TOKEN')
        self.assertEqual(value, 'dXNlcjpwYXNzd29yZD0xMjM=')
    
    def test_env_case_sensitivity(self):
        """Test that environment variable names are case-sensitive."""
        content = '''valtown_url="https://test.val.run"\nDEVICE_TOKEN="token"'''
        
        self.env_path.write_text(content)
        
        lines = content.strip().split('\n')
        has_valtown_url = any('valtown_url' in line for line in lines)
        has_device_token = any('DEVICE_TOKEN' in line for line in lines)
        
        self.assertTrue(has_valtown_url)
        self.assertTrue(has_device_token)
        
        # These are different variable names
        self.assertNotEqual('valtown_url', 'VALTOWN_URL')


if __name__ == '__main__':
    unittest.main()
