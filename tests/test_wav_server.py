import pytest
from wav_server import app
import io


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_upload_wav_success(client):
    """Test successful WAV file upload."""
    # Create a mock WAV file
    data = {
        'file': (io.BytesIO(b'\x52\x49\x46\x46'), 'test_recording.wav')
    }
    
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data


def test_upload_wav_no_file_part(client):
    """Test upload without file part returns 400 error."""
    data = {}
    
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No file part' in response.data


def test_upload_wav_empty_filename(client):
    """Test upload with empty filename returns 400 error."""
    data = {
        'file': (io.BytesIO(b''), '')
    }
    
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No selected file' in response.data


def test_upload_wav_different_extensions(client):
    """Test that non-WAV files are also accepted (server doesn't validate extension)."""
    data = {
        'file': (io.BytesIO(b'test content'), 'test.txt')
    }
    
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data


def test_upload_wav_multiple_files(client):
    """Test upload with multiple files (only first should be processed)."""
    data = {
        'file': [
            (io.BytesIO(b'\x52\x49\x46\x46'), 'first.wav'),
            (io.BytesIO(b'\x52\x49\x46\x46'), 'second.wav')
        ]
    }
    
    response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data
