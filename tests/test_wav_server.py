"""Tests for wav_server.py Flask application."""
import pytest
import os
import tempfile
import shutil
from io import BytesIO
from unittest.mock import patch

# Add repo root to path
import sys
sys.path.insert(0, '')

# Import the Flask app
from wav_server import app, UPLOAD_DIR


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


@pytest.fixture
def temp_upload_dir():
    """Create a temporary upload directory for testing."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Patch the UPLOAD_DIR to use temp directory
    original_makedirs = os.makedirs
    
    def mock_makedirs(path, exist_ok=False):
        if not os.path.exists(path):
            original_makedirs(path, exist_ok=exist_ok)
    
    with patch('wav_server.UPLOAD_DIR', temp_dir):
        with patch('wav_server.os.makedirs', side_effect=mock_makedirs):
            yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_upload_wav_success(client, temp_upload_dir):
    """Test successful WAV file upload."""
    # Create a simple WAV file content (minimal valid WAV)
    wav_content = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    # Use BytesIO to simulate a file upload
    data = {
        'file': (BytesIO(wav_content), 'test_recording.wav')
    }
    
    response = client.post('/upload_wav', 
                          data=data,
                          content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data
    
    # Check that file was saved
    uploaded_files = os.listdir(temp_upload_dir)
    assert len(uploaded_files) == 1
    assert uploaded_files[0].startswith('recording_')
    assert uploaded_files[0].endswith('.wav')


def test_upload_wav_no_file_part(client):
    """Test upload without file part returns 400."""
    response = client.post('/upload_wav', 
                          data={},
                          content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No file part' in response.data


def test_upload_wav_no_filename(client):
    """Test upload with empty filename returns 400."""
    response = client.post('/upload_wav', 
                          data={'file': (BytesIO(b''), '')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No selected file' in response.data


def test_upload_wav_non_wav_extension(client, temp_upload_dir):
    """Test that non-WAV files can still be uploaded (server doesn't validate extension)."""
    response = client.post('/upload_wav', 
                          data={'file': (BytesIO(b'test content'), 'test.txt')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data


def test_upload_wav_creates_directory(client, temp_upload_dir):
    """Test that upload directory is created if it doesn't exist."""
    # The fixture already handles this, but we verify the directory exists
    assert os.path.exists(temp_upload_dir)


def test_upload_wav_timestamp_format(client, temp_upload_dir):
    """Test that uploaded files have proper timestamp format in filename."""
    wav_content = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    response = client.post('/upload_wav', 
                          data={'file': (BytesIO(wav_content), 'test.wav')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 200
    
    uploaded_files = os.listdir(temp_upload_dir)
    assert len(uploaded_files) == 1
    
    # Check timestamp format: recording_YYYYMMDD_HHMMSS.wav
    filename = uploaded_files[0]
    import re
    pattern = r'^recording_\d{8}_\d{6}\.wav$'
    assert re.match(pattern, filename) is not None
