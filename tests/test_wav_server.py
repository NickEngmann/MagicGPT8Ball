"""Tests for wav_server.py Flask application."""
import pytest
import sys
import os
import io

sys.path.insert(0, '')

from wav_server import app, UPLOAD_DIR


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


def test_upload_wav_success(client):
    """Test successful WAV file upload."""
    # Create a dummy WAV file
    data = {
        'file': (io.BytesIO(b'\x52\x49\x46\x46'), 'test.wav')
    }
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data


def test_upload_wav_no_file(client):
    """Test upload without file returns 400."""
    data = {}
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b'No file part' in response.data


def test_upload_wav_empty_filename(client):
    """Test upload with empty filename returns 400."""
    data = {
        'file': (io.BytesIO(b''), '')
    }
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b'No selected file' in response.data
