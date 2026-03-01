"""Tests for wav_server.py Flask application."""
import pytest
import os
import tempfile
import shutil
import io
from unittest.mock import patch

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
    temp_dir = tempfile.mkdtemp()
    with patch('wav_server.UPLOAD_DIR', temp_dir):
        with patch('wav_server.os.makedirs'):
            yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_upload_wav_success(client, temp_upload_dir):
    """Test successful WAV file upload."""
    data = {
        'file': (io.BytesIO(b'\x52\x49\x46\x46'), 'test_recording.wav')
    }
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data


def test_upload_wav_no_file(client, temp_upload_dir):
    """Test upload without file returns 400."""
    data = {}
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b'No file part' in response.data


def test_upload_wav_empty_filename(client, temp_upload_dir):
    """Test upload with empty filename returns 400."""
    data = {
        'file': (io.BytesIO(b'\x52\x49\x46\x46'), '')
    }
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b'No selected file' in response.data


def test_upload_wav_creates_directory(client, temp_upload_dir):
    """Test that upload creates the upload directory if it doesn't exist."""
    data = {
        'file': (io.BytesIO(b'\x52\x49\x46\x46'), 'test_recording.wav')
    }
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    assert response.status_code == 200


def test_upload_wav_generates_timestamped_filename(client, temp_upload_dir):
    """Test that uploaded files get timestamped filenames."""
    data = {
        'file': (io.BytesIO(b'\x52\x49\x46\x46'), 'test_recording.wav')
    }
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
