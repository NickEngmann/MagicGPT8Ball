"""Test suite for wav_server.py Flask application."""
import pytest
import os
import sys
import io
from unittest.mock import patch, MagicMock

# Add repo root to path
sys.path.insert(0, '')

# Mock Flask extensions before importing the app
sys.modules['flask_limiter'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()

from wav_server import app, UPLOAD_DIR


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
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


class TestUploadWavEndpoint:
    """Tests for the /upload_wav endpoint."""

    def test_upload_wav_success(self, client, clean_upload_dir):
        """Test successful WAV file upload."""
        data = {
            'file': (io.BytesIO(b'\x52\x49\x46\x46\x00\x00\x00\x00\x57\x41\x56\x45'), 'test_recording.wav')
        }
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        assert b'File uploaded successfully' in response.data

    def test_upload_wav_no_file_part(self, client, clean_upload_dir):
        """Test upload without file part returns 400 error."""
        data = {}
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert b'No file part' in response.data

    def test_upload_wav_empty_filename(self, client, clean_upload_dir):
        """Test upload with empty filename returns 400 error."""
        data = {
            'file': (b'', '')
        }
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert b'No selected file' in response.data

    def test_upload_wav_creates_file(self, client, clean_upload_dir):
        """Test that upload actually creates a file in the upload directory."""
        data = {
            'file': (b'\x52\x49\x46\x46\x00\x00\x00\x00\x57\x41\x56\x45', 'test_recording.wav')
        }
        client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        # Check that file was created
        assert os.path.exists(UPLOAD_DIR)
        files = os.listdir(UPLOAD_DIR)
        assert len(files) == 1
        assert files[0].startswith('recording_')
        assert files[0].endswith('.wav')

    def test_upload_wav_timestamp_format(self, client, clean_upload_dir):
        """Test that uploaded files have correct timestamp format."""
        data = {
            'file': (b'\x52\x49\x46\x46\x00\x00\x00\x00\x57\x41\x56\x45', 'test_recording.wav')
        }
        client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        files = os.listdir(UPLOAD_DIR)
        assert len(files) == 1
        # Check timestamp format: YYYYMMDD_HHMMSS
        filename = files[0]
        assert len(filename) == len('recording_YYYYMMDD_HHMMSS.wav')

    def test_upload_wav_multiple_files(self, client, clean_upload_dir):
        """Test uploading multiple files."""
        for i in range(3):
            data = {
                'file': (b'\x52\x49\x46\x46\x00\x00\x00\x00\x57\x41\x56\x45', f'test_{i}.wav')
            }
            client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        files = os.listdir(UPLOAD_DIR)
        assert len(files) == 3

    def test_upload_wav_different_content_types(self, client, clean_upload_dir):
        """Test upload with different file content types."""
        # Test with binary WAV data
        data = {
            'file': (b'\x52\x49\x46\x46\x00\x00\x00\x00\x57\x41\x56\x45', 'audio.wav')
        }
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        assert response.status_code == 200

    def test_upload_wav_large_file(self, client, clean_upload_dir):
        """Test upload with larger WAV file."""
        # Create a larger WAV-like file (header + some audio data)
        large_data = b'\x52\x49\x46\x46' + b'\x00' * 1000 + b'\x57\x41\x56\x45'
        data = {
            'file': (large_data, 'large_recording.wav')
        }
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        files = os.listdir(UPLOAD_DIR)
        assert len(files) == 1


class TestAppConfiguration:
    """Tests for Flask app configuration."""

    def test_app_exists(self):
        """Test that the Flask app is created."""
        assert app is not None

    def test_app_testing_mode(self):
        """Test that app can be set to testing mode."""
        app.config['TESTING'] = True
        assert app.config['TESTING'] is True


class TestUploadDirectory:
    """Tests for upload directory handling."""

    def test_upload_dir_exists(self, clean_upload_dir):
        """Test that upload directory exists."""
        assert os.path.exists(UPLOAD_DIR)
        assert os.path.isdir(UPLOAD_DIR)

    def test_upload_dir_is_writable(self, clean_upload_dir):
        """Test that upload directory is writable."""
        test_file = os.path.join(UPLOAD_DIR, 'test_write.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        assert os.path.exists(test_file)
        os.remove(test_file)
