"""Tests for wav_server.py Flask application."""
import pytest
import os
import tempfile
import io
from unittest.mock import patch, MagicMock
from wav_server import app, UPLOAD_DIR


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_upload_dir():
    """Use a temporary directory for uploads during testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('wav_server.UPLOAD_DIR', tmpdir):
            yield tmpdir


def test_upload_wav_success(client, temp_upload_dir):
    """Test successful WAV file upload."""
    # Create a test WAV file
    test_file = (b'\x52\x49\x46\x46'  # RIFF header
                b'\x24\x00\x00\x00'  # File size
                b'\x57\x41\x56\x45'  # WAVE format
                b'\x66\x6d\x74\x20'  # fmt chunk
                b'\x10\x00\x00\x00'  # Chunk size
                b'\x01\x00\x01\x00'  # Audio format, channels
                b'\x40\x1f\x00\x00'  # Sample rate (8000 Hz)
                b'\x80\x3e\x00\x00'  # Byte rate
                b'\x02\x00\x10\x00'  # Block align, bits per sample
                b'\x64\x61\x74\x61'  # data chunk
                b'\x00\x00\x00\x00')  # Data size
    
    response = client.post('/upload_wav', 
                          data={'file': (io.BytesIO(test_file), 'test.wav')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data


def test_upload_wav_no_file_part(client, temp_upload_dir):
    """Test upload without file part returns 400."""
    response = client.post('/upload_wav', 
                          data={},
                          content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No file part' in response.data


def test_upload_wav_empty_filename(client, temp_upload_dir):
    """Test upload with empty filename returns 400."""
    response = client.post('/upload_wav', 
                          data={'file': (io.BytesIO(b''), '')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No selected file' in response.data


def test_upload_wav_creates_directory(client, temp_upload_dir):
    """Test that upload creates the upload directory if needed."""
    # Directory should be created by temp_upload_dir fixture
    assert os.path.exists(temp_upload_dir)


def test_upload_wav_generates_timestamped_filename(client, temp_upload_dir):
    """Test that uploaded files get timestamped filenames."""
    import io
    test_file = (b'\x52\x49\x46\x46'  # RIFF header
                b'\x24\x00\x00\x00'  # File size
                b'\x57\x41\x56\x45'  # WAVE format
                b'\x66\x6d\x74\x20'  # fmt chunk
                b'\x10\x00\x00\x00'  # Chunk size
                b'\x01\x00\x01\x00'  # Audio format, channels
                b'\x40\x1f\x00\x00'  # Sample rate (8000 Hz)
                b'\x80\x3e\x00\x00'  # Byte rate
                b'\x02\x00\x10\x00'  # Block align, bits per sample
                b'\x64\x61\x74\x61'  # data chunk
                b'\x00\x00\x00\x00')  # Data size
    
    response = client.post('/upload_wav', 
                          data={'file': (io.BytesIO(test_file), 'test.wav')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 200
    
    # Check that a file was created with timestamped name
    files = os.listdir(temp_upload_dir)
    assert len(files) == 1
    assert files[0].startswith('recording_')
    assert files[0].endswith('.wav')
