"""
Pytest fixtures for MagicGPT8Ball test suite.

Provides common fixtures for testing Python components including
WAV server, image conversion, and environment generation scripts.
"""

import pytest
import os
import sys
import tempfile
import shutil
import struct
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch


@pytest.fixture
def test_directory():
    """Create a temporary test directory that is cleaned up after tests."""
    test_dir = tempfile.mkdtemp(prefix='magics8ball_test_')
    yield test_dir
    shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture
def wav_upload_dir(test_directory):
    """Create a temporary WAV upload directory."""
    upload_dir = os.path.join(test_directory, 'wav_uploads')
    os.makedirs(upload_dir, exist_ok=True)
    yield upload_dir
    shutil.rmtree(test_directory, ignore_errors=True)


@pytest.fixture
def temp_env_file(test_directory):
    """Create a temporary .env file with test configuration."""
    env_file = os.path.join(test_directory, '.env')
    env_content = """VALTOWN_URL="https://test-app.val.run"
DEVICE_TOKEN="test-device-token-123"
"""
    with open(env_file, 'w') as f:
        f.write(env_content)
    yield env_file
    shutil.rmtree(test_directory, ignore_errors=True)


@pytest.fixture
def temp_env_example(test_directory):
    """Create a temporary .env.example file."""
    env_example = os.path.join(test_directory, '.env.example')
    env_content = """VALTOWN_URL="https://example-valtown-endpoint.val.run"
DEVICE_TOKEN="example-device-token"
"""
    with open(env_example, 'w') as f:
        f.write(env_content)
    yield env_example
    shutil.rmtree(test_directory, ignore_errors=True)


@pytest.fixture
def valid_wav_file(wav_upload_dir):
    """Create a valid WAV file for testing."""
    wav_file = os.path.join(wav_upload_dir, 'valid_test.wav')
    sample_rate = 16000
    channels = 1
    bits = 16
    duration = 1
    
    num_samples = sample_rate * duration
    bytes_per_sample = bits // 8
    block_align = channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    data_size = num_samples * block_align
    file_size = 36 + data_size
    
    with open(wav_file, 'wb') as f:
        f.write(b'RIFF')
        f.write(struct.pack('<I', file_size))
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))
        f.write(struct.pack('<H', 1))
        f.write(struct.pack('<H', channels))
        f.write(struct.pack('<I', sample_rate))
        f.write(struct.pack('<I', byte_rate))
        f.write(struct.pack('<H', block_align))
        f.write(struct.pack('<H', bits))
        f.write(b'data')
        f.write(struct.pack('<I', data_size))
        f.write(b'\x00' * data_size)
    
    yield wav_file
    shutil.rmtree(wav_upload_dir, ignore_errors=True)


@pytest.fixture
def invalid_wav_file(wav_upload_dir):
    """Create an invalid WAV file for testing."""
    wav_file = os.path.join(wav_upload_dir, 'invalid_test.wav')
    with open(wav_file, 'wb') as f:
        f.write(b'RIFF')
        f.write(b'not enough bytes for valid wav')
    yield wav_file
    shutil.rmtree(wav_upload_dir, ignore_errors=True)


@pytest.fixture
def platformio_env_mock():
    """Mock PlatformIO environment object for generate_env.py tests."""
    env_mock = MagicMock()
    
    def get_mock(key):
        project_dir = os.path.join(tempfile.gettempdir(), 'platformio_test_project')
        mappings = {
            'PROJECT_DIR': project_dir,
            'PLATFORMIO_PROJECT_DIR': project_dir
        }
        return mappings.get(key, project_dir)
    
    env_mock.get.side_effect = get_mock
    yield env_mock


@pytest.fixture
def flask_test_client():
    """Create a Flask test client with configured settings."""
    from wav_server import app
    
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_image_file(test_directory):
    """Create a mock JPEG image file for testing."""
    try:
        from PIL import Image
        img_file = os.path.join(test_directory, 'test_image.jpg')
        img = Image.new('RGB', (240, 240), color=(255, 0, 0))
        img.save(img_file, 'JPEG')
        yield img_file
    except ImportError:
        pytest.skip("PIL/Pillow not installed")


@pytest.fixture
def cleanup_after_test(test_directory):
    """Yield directory and ensure cleanup after tests."""
    yield test_directory
    shutil.rmtree(test_directory, ignore_errors=True)


@pytest.fixture
def mock_os_functions():
    """Mock OS functions for file system tests."""
    with patch('os.path.exists') as mock_exists, \
         patch('os.path.join') as mock_join, \
         patch('os.makedirs') as mock_makedirs:
        
        mock_join.side_effect = os.path.join
        mock_exists.return_value = True
        mock_makedirs.return_value = None
        
        yield {
            'exists': mock_exists,
            'join': mock_join,
            'makedirs': mock_makedirs
        }


@pytest.fixture
def mock_shutil_functions():
    """Mock shutil functions for copy operations."""
    with patch('shutil.copy2') as mock_copy:
        yield mock_copy


@pytest.fixture
def sample_wav_data():
    """Provide sample WAV file bytes."""
    sample_rate = 16000
    channels = 1
    bits = 16
    duration = 0.1
    
    num_samples = int(sample_rate * duration)
    bytes_per_sample = bits // 8
    block_align = channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    data_size = num_samples * block_align
    file_size = 36 + data_size
    
    wav_bytes = bytearray()
    wav_bytes.extend(b'RIFF')
    wav_bytes.extend(struct.pack('<I', file_size))
    wav_bytes.extend(b'WAVE')
    wav_bytes.extend(b'fmt ')
    wav_bytes.extend(struct.pack('<I', 16))
    wav_bytes.extend(struct.pack('<H', 1))
    wav_bytes.extend(struct.pack('<H', channels))
    wav_bytes.extend(struct.pack('<I', sample_rate))
    wav_bytes.extend(struct.pack('<I', byte_rate))
    wav_bytes.extend(struct.pack('<H', block_align))
    wav_bytes.extend(struct.pack('<H', bits))
    wav_bytes.extend(b'data')
    wav_bytes.extend(struct.pack('<I', data_size))
    wav_bytes.extend(b'\x00' * data_size)
    
    yield bytes(wav_bytes)


@pytest.fixture
def multiple_wav_files(wav_upload_dir):
    """Create multiple WAV files for batch testing."""
    files_created = []
    
    for i in range(5):
        wav_file = os.path.join(wav_upload_dir, f'test_{i}.wav')
        with open(wav_file, 'wb') as f:
            f.write(b'RIFF' + b'x' * 50 + b'WAVE')
        files_created.append(wav_file)
    
    yield files_created
    shutil.rmtree(wav_upload_dir, ignore_errors=True)


@pytest.fixture
def old_wav_file(wav_upload_dir):
    """Create an old WAV file for cleanup testing."""
    wav_file = os.path.join(wav_upload_dir, 'old_test.wav')
    with open(wav_file, 'wb') as f:
        f.write(b'RIFF' + b'x' * 50 + b'WAVE')
    
    # Set modification time to 48 hours ago
    old_time = datetime.now().timestamp() - (48 * 3600)
    os.utime(wav_file, (old_time, old_time))
    
    yield wav_file
    shutil.rmtree(wav_upload_dir, ignore_errors=True)


@pytest.fixture
def new_wav_file(wav_upload_dir):
    """Create a new WAV file for cleanup testing."""
    wav_file = os.path.join(wav_upload_dir, 'new_test.wav')
    with open(wav_file, 'wb') as f:
        f.write(b'RIFF' + b'x' * 50 + b'WAVE')
    yield wav_file
    shutil.rmtree(wav_upload_dir, ignore_errors=True)


@pytest.fixture
def data_directory(test_directory):
    """Create a data directory for file system tests."""
    data_dir = os.path.join(test_directory, 'data')
    os.makedirs(data_dir, exist_ok=True)
    yield data_dir
    shutil.rmtree(test_directory, ignore_errors=True)


@pytest.fixture
def env_file_in_data_dir(data_directory):
    """Create an .env file in the data directory."""
    env_file = os.path.join(data_directory, '.env')
    with open(env_file, 'w') as f:
        f.write('TEST_VALUE=test')
    yield env_file
    shutil.rmtree(data_directory, ignore_errors=True)


@pytest.fixture
def mocked_datetime():
    """Mock datetime for time-sensitive tests."""
    with patch('datetime.datetime') as mock_datetime:
        mock_now = datetime(2026, 3, 25, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromtimestamp.return_value = mock_now
        yield mock_datetime


@pytest.fixture
def temp_project_structure(test_directory):
    """Create a temporary project structure."""
    project_structure = {
        'src': [],
        'lib': [],
        'data': [],
        'tests': []
    }
    
    for dir_name in project_structure:
        dir_path = os.path.join(test_directory, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        project_structure[dir_name].append(dir_path)
    
    yield project_structure
    shutil.rmtree(test_directory, ignore_errors=True)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Automatically set up test environment before each test."""
    # Ensure test directory exists
    test_dir = tempfile.mkdtemp()
    os.environ['TEST_DIR'] = test_dir
    
    yield
    
    # Cleanup after test
    shutil.rmtree(os.environ.get('TEST_DIR', ''), ignore_errors=True)
    if 'TEST_DIR' in os.environ:
        del os.environ['TEST_DIR']


@pytest.fixture
def json_response_factory():
    """Factory for creating JSON responses."""
    def factory(data, status_code=200):
        response = MagicMock()
        response.status_code = status_code
        response.get_json.return_value = data
        return response
    return factory


@pytest.fixture
def multipart_form_data_factory():
    """Factory for creating multipart form data."""
    def factory(filename, content, content_type='application/octet-stream'):
        return {
            'filename': filename,
            'content': content,
            'content_type': content_type
        }
    return factory


@pytest.fixture
def file_stat_mock():
    """Mock file statistics."""
    with patch('os.stat') as mock_stat:
        mock_stat_result = MagicMock()
        mock_stat_result.st_size = 1024
        mock_stat_result.st_mtime = datetime.now().timestamp()
        mock_stat_result.st_ctime = datetime.now().timestamp()
        mock_stat.return_value = mock_stat_result
        yield mock_stat


@pytest.fixture
def temporary_python_path():
    """Temporarily add a path to sys.path."""
    test_path = tempfile.mkdtemp()
    sys.path.insert(0, test_path)
    
    yield test_path
    
    sys.path.remove(test_path)
    shutil.rmtree(test_path, ignore_errors=True)


@pytest.fixture
def csv_data_file(test_directory):
    """Create a CSV data file for testing."""
    csv_file = os.path.join(test_directory, 'data.csv')
    csv_content = """name,value
test1,100
test2,200
test3,300
"""
    with open(csv_file, 'w') as f:
        f.write(csv_content)
    yield csv_file
    shutil.rmtree(test_directory, ignore_errors=True)


@pytest.fixture
def binary_data_file(test_directory):
    """Create a binary data file for testing."""
    binary_file = os.path.join(test_directory, 'binary.bin')
    with open(binary_file, 'wb') as f:
        f.write(bytes([0x00, 0xFF, 0x12, 0x34, 0xAB, 0xCD]))
    yield binary_file
    shutil.rmtree(test_directory, ignore_errors=True)


@pytest.fixture
def config_file(test_directory):
    """Create a configuration file for testing."""
    config_file = os.path.join(test_directory, 'config.json')
    config_content = '{"setting": "value", "enabled": true}'
    with open(config_file, 'w') as f:
        f.write(config_content)
    yield config_file
    shutil.rmtree(test_directory, ignore_errors=True)


@pytest.fixture
def log_file(test_directory):
    """Create a log file for testing."""
    log_file = os.path.join(test_directory, 'test.log')
    log_content = "2026-03-25 12:00:00 INFO Test log entry\n"
    with open(log_file, 'w') as f:
        f.write(log_content)
    yield log_file
    shutil.rmtree(test_directory, ignore_errors=True)
