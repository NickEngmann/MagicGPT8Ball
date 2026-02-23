import pytest
from wav_server import app
import os
import tempfile

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_upload_wav_success(client):
    """Test successful WAV file upload."""
    # Create a temporary WAV file for testing
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_file.write(b'\x52\x49\x46\x46')  # RIFF header
        temp_file_path = temp_file.name
    
    try:
        with open(temp_file_path, 'rb') as wav_file:
            response = client.post('/upload_wav', 
                                  data={'file': (wav_file, 'test_recording.wav')},
                                  content_type='multipart/form-data')
        
        assert response.status_code == 200
        assert b'File uploaded successfully' in response.data
        
        # Verify file was saved
        uploaded_files = os.listdir('wav_uploads')
        assert len(uploaded_files) >= 1
        assert any('recording_' in f and '.wav' in f for f in uploaded_files)
    finally:
        os.unlink(temp_file_path)

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
                          data={'file': (None, '')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No selected file' in response.data

def test_upload_wav_non_wav_file(client):
    """Test upload with non-WAV file is still accepted (file type not validated)."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        temp_file.write(b'test content')
        temp_file_path = temp_file.name
    
    try:
        with open(temp_file_path, 'rb') as txt_file:
            response = client.post('/upload_wav', 
                                  data={'file': (txt_file, 'test.txt')},
                                  content_type='multipart/form-data')
        
        assert response.status_code == 200
        assert b'File uploaded successfully' in response.data
    finally:
        os.unlink(temp_file_path)
