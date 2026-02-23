import pytest
from wav_server import app, UPLOAD_DIR
import os
import tempfile
import shutil
from io import BytesIO
import time


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
    
    # Override the UPLOAD_DIR module-level variable
    import wav_server
    original_upload_dir = wav_server.UPLOAD_DIR
    wav_server.UPLOAD_DIR = temp_dir
    
    yield temp_dir
    
    # Restore original
    wav_server.UPLOAD_DIR = original_upload_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


def test_upload_wav_success(client, temp_upload_dir):
    """Test successful WAV file upload."""
    # Create a simple WAV file content (minimal valid WAV)
    wav_content = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x80\x3e\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    response = client.post('/upload_wav', 
                          data={'file': (BytesIO(wav_content), 'test_recording.wav')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data
    
    # Verify file was saved
    files = os.listdir(temp_upload_dir)
    assert len(files) == 1
    assert files[0].startswith('recording_')
    assert files[0].endswith('.wav')


def test_upload_wav_no_file(client, temp_upload_dir):
    """Test upload without file returns 400 error."""
    response = client.post('/upload_wav', 
                          data={},
                          content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No file part' in response.data


def test_upload_wav_empty_filename(client, temp_upload_dir):
    """Test upload with empty filename returns 400 error."""
    response = client.post('/upload_wav', 
                          data={'file': (BytesIO(b''), '')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert b'No selected file' in response.data


def test_upload_wav_multiple_files_sequential(client, temp_upload_dir):
    """Test uploading multiple files with a delay to ensure different timestamps."""
    wav_content = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x80\x3e\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    # First upload
    response1 = client.post('/upload_wav', 
                           data={'file': (BytesIO(wav_content), 'test1.wav')},
                           content_type='multipart/form-data')
    assert response1.status_code == 200
    
    # Wait a second to ensure different timestamp
    time.sleep(1.1)
    
    # Second upload
    response2 = client.post('/upload_wav', 
                           data={'file': (BytesIO(wav_content), 'test2.wav')},
                           content_type='multipart/form-data')
    assert response2.status_code == 200
    
    # Verify both files were saved (with different timestamps)
    files = os.listdir(temp_upload_dir)
    assert len(files) == 2
    # Both files should have different timestamps (full filename)
    filenames = [f for f in files if f.startswith('recording_')]
    assert filenames[0] != filenames[1]


def test_upload_wav_different_content_types(client, temp_upload_dir):
    """Test upload with different content types."""
    wav_content = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x80\x3e\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    # Test with explicit content_type parameter
    response = client.post('/upload_wav', 
                          data={'file': (BytesIO(wav_content), 'audio.wav', 'audio/wav')},
                          content_type='multipart/form-data')
    
    assert response.status_code == 200
    
    files = os.listdir(temp_upload_dir)
    assert len(files) == 1
