import pytest
from wav_server import app, UPLOAD_DIR
import os
import tempfile
from unittest.mock import patch, MagicMock
from io import BytesIO
from datetime import datetime


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


@pytest.fixture
def temp_upload_dir():
    """Use a temporary directory for uploads during testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_upload_wav_success(client, temp_upload_dir):
    """Test successful WAV file upload."""
    wav_content = b'RIFF\x00\x00\x00\x00WAVEfmt '
    
    # Patch UPLOAD_DIR to use temp directory
    with patch('wav_server.UPLOAD_DIR', temp_upload_dir):
        response = client.post('/upload_wav', 
                              data={'file': (BytesIO(wav_content), 'test_recording.wav')},
                              content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data


def test_upload_wav_no_file_part(client, temp_upload_dir):
    """Test upload without file part returns 400 error."""
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


def test_upload_wav_creates_file(client, temp_upload_dir):
    """Test that upload actually creates a file."""
    wav_content = b'RIFF\x00\x00\x00\x00WAVEfmt '
    
    with patch('wav_server.UPLOAD_DIR', temp_upload_dir):
        response = client.post('/upload_wav',
                              data={'file': (BytesIO(wav_content), 'test.wav')},
                              content_type='multipart/form-data')
    
    assert response.status_code == 200
    # Check that file was created in upload directory
    files = os.listdir(temp_upload_dir)
    assert len(files) == 1
    assert files[0].startswith('recording_')
    assert files[0].endswith('.wav')


def test_upload_wav_timestamp_format(client, temp_upload_dir):
    """Test that uploaded files have proper timestamp format."""
    wav_content = b'RIFF\x00\x00\x00\x00WAVEfmt '
    
    with patch('wav_server.UPLOAD_DIR', temp_upload_dir):
        response = client.post('/upload_wav',
                              data={'file': (BytesIO(wav_content), 'test.wav')},
                              content_type='multipart/form-data')
    
    assert response.status_code == 200
    files = os.listdir(temp_upload_dir)
    assert len(files) == 1
    # Check timestamp format: YYYYMMDD_HHMMSS
    filename = files[0]
    parts = filename.replace('recording_', '').replace('.wav', '').split('_')
    assert len(parts) == 2
    assert len(parts[0]) == 8  # YYYYMMDD
    assert len(parts[1]) == 6  # HHMMSS


def test_upload_wav_multiple_files(client, temp_upload_dir):
    """Test uploading multiple files with mocked timestamps."""
    wav_content = b'RIFF\x00\x00\x00\x00WAVEfmt '
    
    # Mock datetime to return different timestamps for each call
    mock_datetime = MagicMock()
    mock_datetime.now.side_effect = [
        datetime(2024, 1, 1, 12, 0, 0),
        datetime(2024, 1, 1, 12, 0, 1),  # 1 second later
    ]
    
    with patch('wav_server.UPLOAD_DIR', temp_upload_dir):
        with patch('wav_server.datetime', mock_datetime):
            # First upload
            response1 = client.post('/upload_wav',
                                   data={'file': (BytesIO(wav_content), 'test1.wav')},
                                   content_type='multipart/form-data')
            assert response1.status_code == 200
            
            # Second upload
            response2 = client.post('/upload_wav',
                                   data={'file': (BytesIO(wav_content), 'test2.wav')},
                                   content_type='multipart/form-data')
            assert response2.status_code == 200
    
    files = os.listdir(temp_upload_dir)
    assert len(files) == 2
    # Verify both files exist with different timestamps
    assert 'recording_20240101_120000.wav' in files
    assert 'recording_20240101_120001.wav' in files


def test_upload_wav_invalid_method(client, temp_upload_dir):
    """Test that GET request to upload endpoint returns method not allowed."""
    response = client.get('/upload_wav')
    assert response.status_code == 405


def test_upload_wav_file_content(client, temp_upload_dir):
    """Test that uploaded file content is preserved."""
    wav_content = b'RIFF\x00\x00\x00\x00WAVEfmt test content here'
    
    with patch('wav_server.UPLOAD_DIR', temp_upload_dir):
        response = client.post('/upload_wav',
                              data={'file': (BytesIO(wav_content), 'test.wav')},
                              content_type='multipart/form-data')
    
    assert response.status_code == 200
    files = os.listdir(temp_upload_dir)
    assert len(files) == 1
    
    # Read the saved file and verify content
    saved_path = os.path.join(temp_upload_dir, files[0])
    with open(saved_path, 'rb') as f:
        saved_content = f.read()
    
    assert saved_content == wav_content


def test_upload_wav_special_characters_in_filename(client, temp_upload_dir):
    """Test that special characters in filename are handled."""
    wav_content = b'RIFF\x00\x00\x00\x00WAVEfmt '
    
    with patch('wav_server.UPLOAD_DIR', temp_upload_dir):
        response = client.post('/upload_wav',
                              data={'file': (BytesIO(wav_content), 'my-test_file.wav')},
                              content_type='multipart/form-data')
    
    assert response.status_code == 200
    files = os.listdir(temp_upload_dir)
    assert len(files) == 1
    # The actual filename is generated with timestamp, original filename is ignored
    assert files[0].endswith('.wav')
