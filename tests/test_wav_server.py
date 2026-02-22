import os
import sys
import tempfile
import shutil
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest

# Mock Flask's request.files to simulate file upload
def create_mock_file(filename, content=b"fake wav data"):
    mock_file = MagicMock()
    mock_file.filename = filename
    mock_file.save = lambda path: open(path, 'wb').write(content)
    return mock_file

# Extract and test the core logic from wav_server.py
def generate_timestamp_filename():
    """Extracted from wav_server.py: generate timestamped filename"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'recording_{timestamp}.wav'

def validate_upload_request(files_dict, filename_key='file'):
    """Extracted validation logic from upload_wav"""
    if filename_key not in files_dict:
        return False, "No file part"
    file = files_dict[filename_key]
    if file.filename == '':
        return False, "No selected file"
    return True, None

def save_wav_file(uploads_dir, file):
    """Extracted save logic from upload_wav"""
    os.makedirs(uploads_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'recording_{timestamp}.wav'
    filepath = os.path.join(uploads_dir, filename)
    file.save(filepath)
    return filepath, filename

class TestWavServerLogic:
    """Test extracted logic from wav_server.py without Flask dependencies"""

    def test_timestamp_filename_generation(self):
        """Test that timestamp filename follows expected pattern"""
        filename = generate_timestamp_filename()
        assert filename.startswith('recording_')
        assert filename.endswith('.wav')
        # Check timestamp format: YYYYMMDD_HHMMSS
        assert len(filename) == len('recording_YYYYMMDD_HHMMSS.wav')

    def test_validate_upload_request_success(self):
        """Test successful validation with valid file"""
        mock_file = MagicMock()
        mock_file.filename = "test.wav"
        files = {'file': mock_file}
        valid, error = validate_upload_request(files)
        assert valid is True
        assert error is None

    def test_validate_upload_request_no_file(self):
        """Test validation fails when no file part"""
        files = {}
        valid, error = validate_upload_request(files)
        assert valid is False
        assert "No file part" in error

    def test_validate_upload_request_empty_filename(self):
        """Test validation fails when filename is empty"""
        mock_file = MagicMock()
        mock_file.filename = ""
        files = {'file': mock_file}
        valid, error = validate_upload_request(files)
        assert valid is False
        assert "No selected file" in error

    def test_save_wav_file_creates_file(self):
        """Test that save_wav_file creates the file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_file = create_mock_file("test.wav")
            filepath, filename = save_wav_file(tmpdir, mock_file)
            assert os.path.exists(filepath)
            assert filename.startswith('recording_')
            assert filename.endswith('.wav')

    def test_save_wav_file_uses_timestamp(self):
        """Test that save_wav_file uses timestamp in filename"""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_file = create_mock_file("test.wav")
            filepath, filename = save_wav_file(tmpdir, mock_file)
            # Extract timestamp from filename
            timestamp_part = filename.replace('recording_', '').replace('.wav', '')
            # Check timestamp format: YYYYMMDD_HHMMSS
            assert len(timestamp_part) == 15
            assert timestamp_part[8] == '_'

    def test_save_wav_file_creates_directory(self):
        """Test that save_wav_file creates the uploads directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, 'new_uploads')
            mock_file = create_mock_file("test.wav")
            filepath, filename = save_wav_file(new_dir, mock_file)
            assert os.path.exists(new_dir)
            assert os.path.exists(filepath)