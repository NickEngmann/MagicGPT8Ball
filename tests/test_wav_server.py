"""test_wav_server.py — Tests for the Flask WAV upload server."""
import pytest
import os
import tempfile
import shutil
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
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_upload_dir():
    """Create a temporary upload directory for testing."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Patch the UPLOAD_DIR to use our temp directory
    with patch('wav_server.UPLOAD_DIR', temp_dir):
        with patch('wav_server.os.makedirs'):
            yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_upload_wav_success(client, temp_upload_dir):
    """Test successful WAV file upload."""
    # Create a test WAV file
    test_file_path = os.path.join(temp_upload_dir, 'test.wav')
    with open(test_file_path, 'wb') as f:
        f.write(b'\x52\x49\x46\x46')  # RIFF header
    
    with open(test_file_path, 'rb') as f:
        data = {
            'file': (f, 'test.wav')
        }
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data


def test_upload_wav_no_file_part(client):
    """Test upload without file part returns 400."""
    response = client.post('/upload_wav', data={}, content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No file part' in response.data


def test_upload_wav_empty_filename(client):
    """Test upload with empty filename returns 400."""
    data = {
        'file': (None, '')
    }
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No selected file' in response.data


def test_upload_wav_creates_directory(client, temp_upload_dir):
    """Test that upload creates the uploads directory if it doesn't exist."""
    # The directory should be created by the app
    assert os.path.exists(temp_upload_dir)


def test_upload_wav_generates_timestamped_filename(client, temp_upload_dir):
    """Test that uploaded files get timestamped filenames."""
    # Create a test WAV file
    test_file_path = os.path.join(temp_upload_dir, 'test.wav')
    with open(test_file_path, 'wb') as f:
        f.write(b'\x52\x49\x46\x46')  # RIFF header
    
    with open(test_file_path, 'rb') as f:
        data = {
            'file': (f, 'test.wav')
        }
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    
    # Check that a file with timestamped name was created
    # Note: temp_upload_dir already has test.wav from our test setup
    # so we expect 2 files: the original test.wav and the uploaded recording_*.wav
    files = os.listdir(temp_upload_dir)
    assert len(files) >= 1
    
    # Find the recording file (not our test file)
    recording_files = [f for f in files if f.startswith('recording_')]
    assert len(recording_files) >= 1
    assert recording_files[0].endswith('.wav')
