"""test_wav_server.py — Tests for the MagicGPT8Ball WAV server."""

import pytest
import os
import tempfile
import wave
from pathlib import Path

# Add repo root to path
import sys
sys.path.insert(0, '/workspace/repo')

from wav_server import app, UPLOAD_DIR, MAX_FILE_SIZE, is_valid_wav_file


@pytest.fixture
def client():
    """Create a test client for the WAV server."""
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


@pytest.fixture
def clean_upload_dir():
    """Clean up upload directory before and after tests."""
    # Clean up before test
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            os.remove(os.path.join(UPLOAD_DIR, f))
    yield
    # Clean up after test
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            os.remove(os.path.join(UPLOAD_DIR, f))


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'upload_dir' in data
    assert 'max_file_size_mb' in data


def test_index_endpoint(client):
    """Test the root endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['service'] == 'MagicGPT8Ball WAV Server'
    assert 'version' in data
    assert 'endpoints' in data


def test_upload_wav_success(client, clean_upload_dir):
    """Test successful WAV file upload."""
    # Create a valid WAV file in memory
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        # Create a simple WAV file
        with wave.open(tmp.name, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            # Write some dummy audio data
            wf.writeframes(b'\x00' * 1000)
        
        with open(tmp.name, 'rb') as f:
            data = {'file': (f, 'test_recording.wav')}
            response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        os.remove(tmp.name)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'filename' in data
    assert 'size' in data


def test_upload_no_file(client, clean_upload_dir):
    """Test upload without file returns 400."""
    response = client.post('/upload_wav', data={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_upload_empty_filename(client, clean_upload_dir):
    """Test upload with empty filename returns 400."""
    data = {'file': (None, '')}
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_upload_non_wav_extension(client, clean_upload_dir):
    """Test upload with non-WAV extension returns 400."""
    data = {'file': (b'dummy content', 'test.txt')}
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_upload_invalid_wav_content(client, clean_upload_dir):
    """Test upload with invalid WAV content returns 400."""
    # Create a file with .wav extension but invalid content
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp.write(b'not a valid wav file')
        tmp_path = tmp.name
    
    try:
        with open(tmp_path, 'rb') as f:
            data = {'file': (f, 'invalid.wav')}
            response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    finally:
        os.remove(tmp_path)


def test_is_valid_wav_file():
    """Test the WAV file validation function."""
    # Create a valid WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        with wave.open(tmp.name, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b'\x00' * 1000)
        
        assert is_valid_wav_file(tmp.name) == True
        os.remove(tmp.name)
    
    # Test with invalid file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp.write(b'invalid wav content')
        tmp_path = tmp.name
    
    try:
        assert is_valid_wav_file(tmp_path) == False
    finally:
        os.remove(tmp_path)


def test_max_file_size_configured():
    """Test that max file size is properly configured."""
    # 10MB limit
    assert MAX_FILE_SIZE == 10 * 1024 * 1024


def test_upload_wav_case_insensitive_extension(client, clean_upload_dir):
    """Test that .WAV extension (uppercase) is accepted."""
    # Create a valid WAV file
    with tempfile.NamedTemporaryFile(suffix='.WAV', delete=False) as tmp:
        with wave.open(tmp.name, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b'\x00' * 1000)
        
        with open(tmp.name, 'rb') as f:
            data = {'file': (f, 'TEST_RECORDING.WAV')}
            response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        os.remove(tmp.name)
    
    assert response.status_code == 200
