import sys
import os
import io
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime

# Mock any potential hardware dependencies (even if not present, to be safe)
sys.modules['hardware'] = MagicMock()
sys.modules['hardware.gpio'] = MagicMock()
sys.modules['hardware.audio'] = MagicMock()
sys.modules['hardware.spi'] = MagicMock()
sys.modules['hardware.i2c'] = MagicMock()

# Import after mocking to ensure clean import
import pytest
from flask import Flask
from wav_server import app, UPLOAD_DIR


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestWavServer:
    """Test cases for wav_server.py functionality."""

    def _create_minimal_wav(self):
        """Create a minimal valid WAV file in memory."""
        # Minimal WAV header (44 bytes) + 1 second of silence (mono, 8kHz, 8-bit)
        # RIFF header
        wav_data = b'RIFF'
        wav_data += (36 + 8000).to_bytes(4, 'little')  # File size - 8
        wav_data += b'WAVE'
        # fmt chunk
        wav_data += b'fmt '
        wav_data += (16).to_bytes(4, 'little')  # Chunk size
        wav_data += (1).to_bytes(2, 'little')   # Audio format (1 = PCM)
        wav_data += (1).to_bytes(2, 'little')   # Number of channels
        wav_data += (8000).to_bytes(4, 'little')  # Sample rate
        wav_data += (8000).to_bytes(4, 'little')  # Byte rate
        wav_data += (1).to_bytes(2, 'little')   # Block align
        wav_data += (8).to_bytes(2, 'little')   # Bits per sample
        # data chunk
        wav_data += b'data'
        wav_data += (8000).to_bytes(4, 'little')  # Data size
        wav_data += b'\x80' * 8000  # Silence (8-bit samples center at 0x80)
        return wav_data

    def test_upload_wav_success(self, client):
        """Test successful WAV file upload."""
        # Create a minimal valid WAV file in memory
        wav_data = self._create_minimal_wav()
        data = {
            'file': (io.BytesIO(wav_data), 'test_recording.wav')
        }
        
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        assert b'File uploaded successfully' in response.data
        
        # Verify file was saved in UPLOAD_DIR
        uploaded_files = os.listdir(UPLOAD_DIR)
        assert len(uploaded_files) == 1
        assert uploaded_files[0].startswith('recording_')
        assert uploaded_files[0].endswith('.wav')
        
        # Clean up
        os.remove(os.path.join(UPLOAD_DIR, uploaded_files[0]))

    def test_upload_wav_creates_upload_directory(self, client):
        """Test that upload directory is created if it doesn't exist."""
        # Remove the upload directory if it exists
        if os.path.exists(UPLOAD_DIR):
            import shutil
            shutil.rmtree(UPLOAD_DIR)
        
        # Verify directory doesn't exist
        assert not os.path.exists(UPLOAD_DIR)
        
        # Create a minimal valid WAV file in memory
        wav_data = self._create_minimal_wav()
        data = {
            'file': (io.BytesIO(wav_data), 'test_recording.wav')
        }
        
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        assert b'File uploaded successfully' in response.data
        
        # Verify directory was created
        assert os.path.exists(UPLOAD_DIR)
        
        # Verify file was saved
        uploaded_files = os.listdir(UPLOAD_DIR)
        assert len(uploaded_files) == 1
        
        # Clean up
        os.remove(os.path.join(UPLOAD_DIR, uploaded_files[0]))
        os.rmdir(UPLOAD_DIR)

    def test_upload_wav_no_file_part(self, client):
        """Test upload fails when no file part is provided."""
        data = {}
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert b'No file part' in response.data

    def test_upload_wav_empty_filename(self, client):
        """Test upload fails when filename is empty."""
        data = {
            'file': (io.BytesIO(b''), '')
        }
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert b'No selected file' in response.data

    def test_upload_wav_invalid_file_type(self, client):
        """Test upload fails for non-WAV files."""
        data = {
            'file': (io.BytesIO(b'test content'), 'test.txt')
        }
        response = client.post('/upload_wav', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert b'Invalid file type' in response.data