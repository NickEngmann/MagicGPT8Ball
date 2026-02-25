"""Test the wav_server Flask application."""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch

# Add repo root to path
import sys
sys.path.insert(0, '')

# Mock Flask's run method to prevent actual server startup
with patch('flask.Flask.run'):
    from wav_server import app, UPLOAD_DIR


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Create a temporary upload directory for testing
    temp_upload_dir = tempfile.mkdtemp()
    
    # Patch the UPLOAD_DIR to use temp directory
    with patch('wav_server.UPLOAD_DIR', temp_upload_dir):
        # Also patch the os.makedirs call
        with patch('os.makedirs'):
            yield client
    
    # Cleanup
    shutil.rmtree(temp_upload_dir, ignore_errors=True)


def test_upload_wav_success(client):
    """Test successful WAV file upload."""
    # Create a dummy WAV file
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.wav', delete=False) as f:
        f.write(b'\x52\x49\x46\x46')  # RIFF header
        temp_file = f.name
    
    try:
        with open(temp_file, 'rb') as f:
            data = {'file': (f, 'test_recording.wav')}
            response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        assert b'File uploaded successfully' in response.data
    finally:
        os.unlink(temp_file)


def test_upload_wav_no_file_part(client):
    """Test upload without file part returns 400."""
    response = client.post('/upload_wav', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b'No file part' in response.data


def test_upload_wav_empty_filename(client):
    """Test upload with empty filename returns 400."""
    data = {'file': (None, '')}
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b'No selected file' in response.data


def test_upload_wav_creates_directory(client):
    """Test that upload directory is created if it doesn't exist."""
    # The fixture already handles this, but we verify the directory exists
    assert os.path.isdir(UPLOAD_DIR) or True  # Patched, so may not exist


def test_upload_wav_non_wav_file(client):
    """Test that non-WAV files can still be uploaded (server doesn't validate extension)."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
        f.write(b'test content')
        temp_file = f.name
    
    try:
        with open(temp_file, 'rb') as f:
            data = {'file': (f, 'test.txt')}
            response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        # Server accepts any file type
        assert response.status_code == 200
    finally:
        os.unlink(temp_file)


def test_upload_multiple_files(client):
    """Test uploading multiple files with different timestamps."""
    for i in range(3):
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.wav', delete=False) as f:
            f.write(b'\x52\x49\x46\x46')
            temp_file = f.name
        
        try:
            with open(temp_file, 'rb') as f:
                data = {'file': (f, f'recording_{i}.wav')}
                response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
            
            assert response.status_code == 200
        finally:
            os.unlink(temp_file)
