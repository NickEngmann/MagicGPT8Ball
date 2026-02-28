import pytest
from wav_server import app, UPLOAD_DIR, allowed_file
import os
import tempfile

def test_upload_route_exists():
    """Test that the upload route is defined"""
    with app.test_client() as client:
        response = client.post('/upload_wav')
        assert response.status_code == 400  # No file provided

def test_upload_with_file():
    """Test uploading a WAV file"""
    with app.test_client() as client:
        # Create a proper test file using TemporaryFile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(b'\x00' * 100)
            tmp_path = tmp.name
        
        try:
            with open(tmp_path, 'rb') as f:
                data = {
                    'file': (f, 'test.wav')
                }
                response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
            assert response.status_code == 200
            assert b'successfully' in response.data
        finally:
            os.unlink(tmp_path)

def test_upload_without_file():
    """Test upload without file returns 400"""
    with app.test_client() as client:
        response = client.post('/upload_wav', data={}, content_type='multipart/form-data')
        assert response.status_code == 400

def test_upload_empty_filename():
    """Test upload with empty filename returns 400"""
    with app.test_client() as client:
        data = {
            'file': (b'', '')
        }
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

def test_upload_directory_created():
    """Test that upload directory is created"""
    assert os.path.exists(UPLOAD_DIR)

def test_allowed_file_function():
    """Test the allowed_file function"""
    assert allowed_file('test.wav') == True
    assert allowed_file('test.WAV') == True
    assert allowed_file('test.mp3') == False
    assert allowed_file('noextension') == False
    assert allowed_file('.wav') == True

def test_health_endpoint():
    """Test the health check endpoint"""
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
        assert b'healthy' in response.data

def test_list_uploads_endpoint():
    """Test the list uploads endpoint"""
    with app.test_client() as client:
        response = client.get('/uploads')
        assert response.status_code == 200
