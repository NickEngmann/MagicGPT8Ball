#!/usr/bin/env python3
"""Unit tests for wav_server.py using standard library unittest."""

import unittest
import os
import sys
import tempfile
import shutil
from io import BytesIO
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from wav_server import app, UPLOAD_DIR


class TestWavServer(unittest.TestCase):
    """Test cases for the WAV server."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.upload_dir = os.path.join(self.temp_dir, 'wav_uploads')
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Create test client
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = self.upload_dir
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_app_initialization(self):
        """Test that the app initializes correctly."""
        self.assertIsNotNone(app)
        self.assertEqual(app.config['TESTING'], True)
    
    def test_upload_directory_created(self):
        """Test that upload directory is created."""
        self.assertTrue(os.path.exists(self.upload_dir))
    
    def test_upload_endpoint_exists(self):
        """Test that upload endpoint is accessible."""
        response = self.client.get('/')
        # The app doesn't have a root endpoint, so this should return 404
        self.assertEqual(response.status_code, 404)
    
    def test_upload_post_endpoint(self):
        """Test the upload POST endpoint."""
        # Create a mock WAV file
        wav_content = b'RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00data\x00\x00\x00\x00'
        
        response = self.client.post('/upload', data={
            'file': (BytesIO(wav_content), 'test.wav')
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'File uploaded successfully')
    
    def test_upload_with_invalid_file(self):
        """Test upload with non-WAV file."""
        text_content = b'This is not a WAV file'
        
        response = self.client.post('/upload', data={
            'file': (BytesIO(text_content), 'test.txt')
        })
        
        # Should still succeed since we don't validate file type
        self.assertEqual(response.status_code, 200)
    
    def test_upload_no_file_provided(self):
        """Test upload without providing a file."""
        response = self.client.post('/upload')
        self.assertEqual(response.status_code, 400)
    
    def test_file_saved_to_correct_directory(self):
        """Test that uploaded file is saved to the correct directory."""
        wav_content = b'RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00data\x00\x00\x00\x00'
        
        filename = 'test_upload.wav'
        response = self.client.post('/upload', data={
            'file': (BytesIO(wav_content), filename)
        })
        
        self.assertEqual(response.status_code, 200)
        saved_path = os.path.join(self.upload_dir, filename)
        self.assertTrue(os.path.exists(saved_path))
    
    def test_upload_preserves_filename(self):
        """Test that the original filename is preserved."""
        wav_content = b'RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00data\x00\x00\x00\x00'
        
        filename = 'my_custom_name.wav'
        response = self.client.post('/upload', data={
            'file': (BytesIO(wav_content), filename)
        })
        
        self.assertEqual(response.status_code, 200)
        saved_path = os.path.join(self.upload_dir, filename)
        self.assertTrue(os.path.exists(saved_path))


if __name__ == '__main__':
    unittest.main()
