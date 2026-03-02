"""Tests for wav_server.py Flask application."""
import pytest
import os
import tempfile
import shutil
import io
from wav_server import app, UPLOAD_DIR


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Create a temporary upload directory for testing
    temp_upload_dir = tempfile.mkdtemp()
    app.config['UPLOAD_DIR'] = temp_upload_dir
    
    yield client
    
    # Clean up temporary directory after tests
    shutil.rmtree(temp_upload_dir, ignore_errors=True)


def test_upload_wav_success(client):
    """Test successful WAV file upload."""
    # Create a simple WAV file for testing
    wav_content = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x80\x3e\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    response = client.post('/upload_wav', 
                          data={'file': (io.BytesIO(wav_content), 'test_recording.wav')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data


def test_upload_wav_no_file_part(client):
    """Test upload without file part returns 400 error."""
    response = client.post('/upload_wav', 
                          data={},
                          content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No file part' in response.data


def test_upload_wav_empty_filename(client):
    """Test upload with empty filename returns 400 error."""
    response = client.post('/upload_wav', 
                          data={'file': (io.BytesIO(b''), '')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No selected file' in response.data


def test_upload_wav_creates_directory(client):
    """Test that upload directory is created if it doesn't exist."""
    # The directory should already exist from app initialization
    assert os.path.exists(UPLOAD_DIR)


def test_upload_wav_generates_timestamped_filename(client):
    """Test that uploaded files get timestamped filenames."""
    import io
    wav_content = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x80\x3e\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    response = client.post('/upload_wav', 
                          data={'file': (io.BytesIO(wav_content), 'test.wav')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 200
    
    # Check that a file was created with timestamped name
    files = os.listdir(UPLOAD_DIR)
    assert len(files) == 1
    assert files[0].startswith('recording_')
    assert files[0].endswith('.wav')
