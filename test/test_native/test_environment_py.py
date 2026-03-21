"""
Unit tests for Environment class functionality
Tests environment variable loading and retrieval
"""

import sys

# Test classes that mimic Environment behavior
class Environment:
    """Environment implementation for testing"""
    
    _valtownUrl = ""
    _deviceToken = ""
    
    @classmethod
    def reset(cls):
        cls._valtownUrl = ""
        cls._deviceToken = ""
        
    @classmethod
    def setEnv(cls, key, value):
        if key == "VALTOWN_URL":
            cls._valtownUrl = value
        if key == "DEVICE_TOKEN":
            cls._deviceToken = value
            
    @classmethod
    def getEnv(cls, key):
        if key == "VALTOWN_URL":
            return cls._valtownUrl
        if key == "DEVICE_TOKEN":
            return cls._deviceToken
        return ""
        
    @classmethod
    def parseEnvLine(cls, line):
        """Parse a single environment variable line"""
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith("#"):
            return False
            
        separator_pos = line.find('=')
        if separator_pos <= 0:
            return False
            
        key = line[:separator_pos].strip()
        value = line[separator_pos + 1:].strip()
        
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
            
        cls.setEnv(key, value)
        return True

def test_environment_get_valtown_url():
    """Test: getEnv returns VALTOWN_URL correctly"""
    Environment.reset()
    Environment.setEnv("VALTOWN_URL", "https://example.com/api")
    
    url = Environment.getEnv("VALTOWN_URL")
    assert url == "https://example.com/api"

def test_environment_get_device_token():
    """Test: getEnv returns DEVICE_TOKEN correctly"""
    Environment.reset()
    Environment.setEnv("DEVICE_TOKEN", "secret_token_123")
    
    token = Environment.getEnv("DEVICE_TOKEN")
    assert token == "secret_token_123"

def test_environment_get_unknown_key():
    """Test: getEnv returns empty string for unknown keys"""
    Environment.reset()
    Environment.setEnv("VALTOWN_URL", "https://example.com/api")
    
    result = Environment.getEnv("UNKNOWN_KEY")
    assert result == ""

def test_environment_parse_env_line():
    """Test: parseEnvLine correctly parses environment variables"""
    Environment.reset()
    
    assert Environment.parseEnvLine("VALTOWN_URL=https://api.example.com") == True
    assert Environment.getEnv("VALTOWN_URL") == "https://api.example.com"
    
    Environment.reset()
    assert Environment.parseEnvLine("DEVICE_TOKEN=abc123xyz") == True
    assert Environment.getEnv("DEVICE_TOKEN") == "abc123xyz"

def test_environment_parse_env_line_with_quotes():
    """Test: parseEnvLine handles quoted values"""
    Environment.reset()
    
    assert Environment.parseEnvLine('DEVICE_TOKEN="my token value"') == True
    assert Environment.getEnv("DEVICE_TOKEN") == "my token value"

def test_environment_parse_empty_line():
    """Test: parseEnvLine returns False for empty lines"""
    Environment.reset()
    assert Environment.parseEnvLine("") == False
    assert Environment.parseEnvLine("   ") == False

def test_environment_parse_comment():
    """Test: parseEnvLine returns False for comments"""
    Environment.reset()
    assert Environment.parseEnvLine("# This is a comment") == False
    assert Environment.parseEnvLine("   # Indented comment") == False

def test_environment_parse_invalid_line():
    """Test: parseEnvLine returns False for invalid lines"""
    Environment.reset()
    assert Environment.parseEnvLine("NO_EQUALS_SIGN") == False
    assert Environment.parseEnvLine("=") == False
    assert Environment.parseEnvLine("KEY=") == True  # Valid but empty value
    assert Environment.getEnv("KEY") == ""

def test_environment_multiple_vars():
    """Test: Multiple environment variables can be set"""
    Environment.reset()
    
    Environment.setEnv("VALTOWN_URL", "https://api.example.com")
    Environment.setEnv("DEVICE_TOKEN", "token123")
    
    assert Environment.getEnv("VALTOWN_URL") == "https://api.example.com"
    assert Environment.getEnv("DEVICE_TOKEN") == "token123"

def test_environment_overwrite_values():
    """Test: Environment variables can be overwritten"""
    Environment.reset()
    
    Environment.setEnv("VALTOWN_URL", "https://first.com")
    Environment.setEnv("VALTOWN_URL", "https://second.com")
    
    assert Environment.getEnv("VALTOWN_URL") == "https://second.com"

if __name__ == "__main__":
    # Run all tests
    tests = [
        test_environment_get_valtown_url,
        test_environment_get_device_token,
        test_environment_get_unknown_key,
        test_environment_parse_env_line,
        test_environment_parse_env_line_with_quotes,
        test_environment_parse_empty_line,
        test_environment_parse_comment,
        test_environment_parse_invalid_line,
        test_environment_multiple_vars,
        test_environment_overwrite_values,
    ]
    
    failed = 0
    passed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Exception - {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    sys.exit(0 if failed == 0 else 1)
