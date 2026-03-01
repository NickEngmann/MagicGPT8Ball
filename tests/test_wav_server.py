"""Tests for wav_server.py Flask application."""
import pytest
import io
from wav_server import app
from werkzeug.datastructures import FileStorage


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    return app.test_client()


def create_wav_content():
    """Create minimal valid WAV file content."""
    wav_content = b'\x52\x49\x46\x46'  # RIFF
    wav_content += b'\x24\x00\x00\x00'  # file size
    wav_content += b'\x57\x41\x56\x45'  # WAVE
    wav_content += b'\x66\x6d\x74\x20'  # fmt 
    wav_content += b'\x10\x00\x00\x00'  # chunk size
    wav_content += b'\x01\x00\x01\x00'  # audio format, channels
    wav_content += b'\x40\x1f\x00\x00'  # sample rate (8000 Hz)
    wav_content += b'\x40\x1f\x00\x00'  # byte rate
    wav_content += b'\x02\x00\x10\x00'  # block align, bits per sample
    wav_content += b'\x64\x61\x74\x61'  # data
    wav_content += b'\x00\x00\x00\x00'  # data size
    return wav_content


def test_upload_wav_success(client, tmp_path):
    """Test successful WAV file upload."""
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        wav_content = create_wav_content()
        file_storage = FileStorage(io.BytesIO(wav_content), filename='test_recording.wav')
        
        response = client.post('/upload_wav', 
                               data={'file': file_storage},
                               content_type='multipart/form-data')
        
        assert response.status_code == 200
        assert b'File uploaded successfully' in response.data
        
        # Verify file was created
        upload_dir = tmp_path / 'wav_uploads'
        upload_dir.mkdir(exist_ok=True)
        files = list(upload_dir.glob('*.wav'))
        assert len(files) == 1
    finally:
        os.chdir(original_cwd)


def test_upload_wav_no_file_part(client, tmp_path):
    """Test upload without file part returns 400."""
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        response = client.post('/upload_wav',
                               data={},
                               content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert b'No file part' in response.data
    finally:
        os.chdir(original_cwd)


def test_upload_wav_empty_filename(client, tmp_path):
    """Test upload with empty filename returns 400."""
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        file_storage = FileStorage(io.BytesIO(b''), filename='')
        response = client.post('/upload_wav',
                               data={'file': file_storage},
                               content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert b'No selected file' in response.data
    finally:
        os.chdir(original_cwd)
