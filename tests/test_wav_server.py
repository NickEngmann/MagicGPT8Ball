"""Test the Flask WAV server application."""
import pytest
import sys
import os
from io import BytesIO

# Add the repo root to the path
sys.path.insert(0, '')

from wav_server import app, allowed_file, UPLOAD_DIR


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


def test_allowed_file():
    """Test the allowed_file function."""
    # Valid files
    assert allowed_file('recording.wav') is True
    assert allowed_file('test.WAV') is True
    assert allowed_file('audio.file.wav') is True
    
    # Invalid files
    assert allowed_file('recording.mp3') is False
    assert allowed_file('no_extension') is False
    assert allowed_file('.wav') is True  # Hidden file with wav extension


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'upload_dir' in data


def test_list_uploads(client):
    """Test the list uploads endpoint."""
    response = client.get('/uploads')
    assert response.status_code == 200
    data = response.get_json()
    assert 'files' in data
    assert 'count' in data


def test_upload_no_file(client):
    """Test upload without a file."""
    response = client.post('/upload_wav')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_upload_empty_filename(client):
    """Test upload with empty filename."""
    response = client.post('/upload_wav', data={'file': (BytesIO(b''), '')})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_upload_invalid_file_type(client):
    """Test upload with invalid file type."""
    response = client.post('/upload_wav', data={
        'file': (b'test content', 'test.mp3', 'audio/mpeg')
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'wav' in data['error'].lower()


def test_upload_valid_wav_file(client):
    """Test upload with a valid WAV file."""
    # Create a minimal WAV file header (44 bytes)
    wav_content = b'\x52\x49\x46\x46'  # RIFF
    wav_content += b'\x00\x00\x00\x00'  # File size
    wav_content += b'\x57\x41\x56\x45'  # WAVE
    wav_content += b'\x66\x6D\x74\x20'  # fmt 
    wav_content += b'\x10\x00\x00\x00'  # Subchunk1 size
    wav_content += b'\x01\x00\x01\x00'  # Audio format, channels
    wav_content += b'\x40\x1F\x00\x00'  # Sample rate (8000 Hz)
    wav_content += b'\x40\x1F\x00\x00'  # Byte rate
    wav_content += b'\x01\x00\x08\x00'  # Block align, bits per sample
    wav_content += b'\x64\x61\x74\x61'  # data
    wav_content += b'\x04\x00\x00\x00'  # Subchunk2 size
    wav_content += b'\x00\x00\x00\x00'  # Sample data
    
    response = client.post('/upload_wav', data={
        'file': (wav_content, 'recording.wav', 'audio/wav')
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'filename' in data
    assert 'filepath' in data
    assert 'recording' in data['filename']


def test_file_size_limit(client):
    """Test that large files are rejected."""
    # Create a file larger than 10MB
    large_content = b'x' * (11 * 1024 * 1024)  # 11 MB
    response = client.post('/upload_wav', data={'file': (large_content, 'large.wav')})
    # Flask should reject this before it gets to the route handler
    assert response.status_code in [400, 413]
