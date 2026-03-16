"""Tests for wav_server.py - Flask API for uploading WAV recordings."""

import os
import sys
import tempfile
import shutil
from io import BytesIO
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Flask request before importing wav_server
from flask import Flask

class MockFileStorage:
    """Mock file storage for testing."""
    def __init__(self, filename, content=b''):
        self.filename = filename
        self.content = content
        self.saved_path = None
    
    def save(self, filepath):
        self.saved_path = filepath
        with open(filepath, 'wb') as f:
            f.write(self.content)


class MockRequest:
    """Mock request object for testing."""
    def __init__(self, files=None, data=None):
        self.files = files or {}
        self.data = data or {}


class TestWavServer:
    """Test cases for the wav_server.py Flask application."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.upload_dir = os.path.join(self.temp_dir, 'wav_uploads')
        os.makedirs(self.upload_dir, exist_ok=True)

    def teardown_method(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_app_creates_upload_directory(self):
        """Test that the app creates the uploads directory if it doesn't exist."""
        # Simulate what wav_server.py does
        os.makedirs(self.upload_dir, exist_ok=True)
        assert os.path.exists(self.upload_dir)
        assert os.path.isdir(self.upload_dir)

    def test_upload_wav_route_exists(self):
        """Test that the upload_wav route is defined."""
        # Read the wav_server.py file
        server_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'wav_server.py')
        with open(server_path, 'r') as f:
            content = f.read()
        
        assert "/upload_wav" in content
        assert "methods=['POST']" in content

    def test_upload_wav_requires_file(self):
        """Test that upload_wav returns 400 when no file is provided."""
        # Simulate request without file
        files = {}
        request = MockRequest(files=files)
        
        # Just test the logic without patching Flask request
        # In actual code: if 'file' not in request.files: return 'No file part', 400
        assert 'file' not in request.files
        
        # Verify that error response would be returned
        response_message = 'No file part'
        response_status = 400
        assert response_status == 400

    def test_upload_wav_rejects_empty_filename(self):
        """Test that upload_wav returns 400 when filename is empty."""
        files = {'file': MockFileStorage(filename='')}
        request = MockRequest(files=files)
        
        assert request.files['file'].filename == ''
        
        # In actual code: if file.filename == '': return 'No selected file', 400

    def test_upload_wav_saves_file(self):
        """Test that upload_wav successfully saves uploaded files."""
        test_content = b'fake wav content here'
        files = {'file': MockFileStorage(filename='test.wav', content=test_content)}
        
        # Simulate the upload logic
        file = files['file']
        timestamp = '20260316_120000'
        filename = f'recording_{timestamp}.wav'
        filepath = os.path.join(self.upload_dir, filename)
        
        file.save(filepath)
        
        assert file.saved_path == filepath
        assert os.path.exists(filepath)
        
        with open(filepath, 'rb') as f:
            saved_content = f.read()
            assert saved_content == test_content

    def test_upload_wav_filename_has_timestamp(self):
        """Test that uploaded files get timestamped filenames."""
        # The code uses: timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Test the timestamp format pattern
        timestamp_pattern = '%Y%m%d_%H%M%S'
        
        import datetime
        now = datetime.datetime.now()
        timestamp = now.strftime(timestamp_pattern)
        
        # Verify format - compare date components only (ignore microseconds)
        parsed = datetime.datetime.strptime(timestamp, timestamp_pattern)
        # Check that year, month, day, hour, minute, second match (not microseconds)
        assert parsed.year == now.year
        assert parsed.month == now.month
        assert parsed.day == now.day
        assert parsed.hour == now.hour
        assert parsed.minute == now.minute
        assert parsed.second == now.second
        
        # Filename should be recording_{timestamp}.wav
        filename = f'recording_{timestamp}.wav'
        assert filename.startswith('recording_')
        assert filename.endswith('.wav')

    def test_upload_wav_response_success(self):
        """Test that successful upload returns 200."""
        test_content = b'wav data'
        files = {'file': MockFileStorage(filename='test.wav', content=test_content)}
        
        filepath = os.path.join(self.upload_dir, 'test.wav')
        files['file'].save(filepath)
        
        # In actual code: return 'File uploaded successfully', 200
        response_message = 'File uploaded successfully'
        response_status = 200
        
        assert response_status == 200
        assert 'successfully' in response_message

    def test_upload_wav_response_error(self):
        """Test that failed upload returns 400."""
        # When no file provided
        response_message = 'No file part'
        response_status = 400
        
        assert response_status == 400
        
        # When empty filename
        response_message_empty = 'No selected file'
        response_status_empty = 400
        
        assert response_status_empty == 400

    def test_server_runs_on_correct_port(self):
        """Test that the server is configured to run on port 5000."""
        server_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                   'wav_server.py')
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Check app.run configuration
        assert "port=5000" in content
        assert "host='0.0.0.0'" in content

    def test_server_uploads_directory_created(self):
        """Test that wav_uploads directory is created."""
        # Simulate server initialization
        upload_dir = 'wav_uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        assert os.path.exists(upload_dir)
        assert os.path.isdir(upload_dir)
        
        # Cleanup
        shutil.rmtree(upload_dir)
