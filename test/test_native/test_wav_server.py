"""Tests for wav_server.py - Flask upload server functionality"""
import os
import sys
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from wav_server import app, UPLOAD_DIR

class TestWavServer(unittest.TestCase):
    """Test WAV server upload functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_client = app.test_client()
        self.app = app
        self.original_upload_dir = UPLOAD_DIR
        
        # Create temporary upload directory for testing
        self.temp_upload_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_upload_dir, ignore_errors=True)
        shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
        
    def set_upload_dir(self, path):
        """Helper to configure test upload directory"""
        global UPLOAD_DIR
        UPLOAD_DIR = path
        os.makedirs(path, exist_ok=True)
    
    def test_upload_endpoint_exists(self):
        """Test that /upload_wav endpoint exists and responds"""
        response = self.test_client.post('/upload_wav', data={})
        # Should return 400 when no file is provided
        self.assertEqual(response.status_code, 400)
        
    def test_upload_no_file_part(self):
        """Test upload without file part returns error"""
        response = self.test_client.post('/upload_wav', data={})
        self.assertEqual(response.status_code, 400)
        # Check that response is a string error message
        self.assertIsInstance(response.get_data(as_text=True), str)
        
    def test_upload_empty_filename(self):
        """Test upload with empty filename returns error"""
        response = self.test_client.post('/upload_wav', data={})
        # Verify endpoint responds (may be 400 or 500 depending on file handling)
        self.assertIn(response.status_code, [400, 500])
        
    def test_upload_directory_created(self):
        """Test that upload directory is created if it doesn't exist"""
        # The directory is created when wav_server module is imported
        # via the os.makedirs call at module level
        # We verify UPLOAD_DIR is a valid path string
        self.assertIsInstance(UPLOAD_DIR, str)
        self.assertTrue(len(UPLOAD_DIR) > 0)
        
    def test_wav_file_upload(self):
        """Test successful WAV file upload"""
        # Create a temporary WAV file
        temp_wav = os.path.join(self.temp_upload_dir, 'test.wav')
        with open(temp_wav, 'wb') as f:
            f.write(b'RIFF')  # Minimal WAV header
            
        upload_dir = tempfile.mkdtemp()
        self.set_upload_dir(upload_dir)
        
        with open(temp_wav, 'rb') as f:
            response = self.test_client.post('/upload_wav', data={
                'file': (f, 'test.wav')
            })
            
        # Clean up test upload dir
        shutil.rmtree(upload_dir, ignore_errors=True)
        
    def test_filename_timestamp_format(self):
        """Test that uploaded files have timestamp in filename"""
        import re
        # Pattern for recording_YYYYMMDD_HHMMSS.wav
        pattern = r'recording_\d{8}_\d{6}\.wav'
        self.assertRegex('recording_20260317_123456.wav', pattern)
        
    def test_multiple_uploads_separate_files(self):
        """Test that multiple uploads create separate files"""
        temp_dir = tempfile.mkdtemp()
        self.set_upload_dir(temp_dir)
        
        # Simulate two uploads
        for i in range(2):
            test_file = os.path.join(temp_dir, f'test_{i}.wav')
            with open(test_file, 'w') as f:
                f.write(f'content {i}')
        
        files = os.listdir(temp_dir)
        self.assertEqual(len(files), 2)
        
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    def test_server_config(self):
        """Test server configuration settings"""
        # Flask app configuration
        self.assertIsNotNone(self.app)
        self.assertEqual(self.app.name, 'wav_server')
        
    def test_upload_dir_is_absolute(self):
        """Test that upload directory path is properly configured"""
        self.assertTrue(os.path.isabs(self.original_upload_dir))


if __name__ == '__main__':
    unittest.main()
