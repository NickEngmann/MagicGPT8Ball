#!/usr/bin/env python3
"""
Tests for wav_server.py - WAV file upload Flask server
"""

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wav_server import app, UPLOAD_DIR, set_upload_dir, get_upload_dir


class TestWavServer(unittest.TestCase):
    """Test cases for wav_server.py Flask application"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for uploads during testing
        self.test_upload_dir = tempfile.mkdtemp()
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Set upload directory for this test
        set_upload_dir(self.test_upload_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_upload_dir, ignore_errors=True)

    def test_upload_wav_success(self):
        """Test successful WAV file upload"""
        wav_data = b'RIFFtest WAV data'
        
        response = self.client.post('/upload_wav',
                                   data={'file': (BytesIO(wav_data), 'test_recording.wav')})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'File uploaded successfully')
        
        # Check that file was saved
        files = os.listdir(self.test_upload_dir)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('.wav'))
    
    def test_upload_no_file_returns_400(self):
        """Test upload without file returns 400 error"""
        response = self.client.post('/upload_wav', data={})
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_data(as_text=True), 'No file part')
    
    def test_upload_empty_filename_returns_400(self):
        """Test upload with empty filename returns 400 error"""
        response = self.client.post('/upload_wav',
                                   data={'file': (BytesIO(b'test'), '')})
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_data(as_text=True), 'No selected file')
    
    def test_upload_creates_file_with_timestamp(self):
        """Test that uploaded files have timestamp in filename"""
        wav_data = b'RIFFtest WAV data with more content'
        
        response = self.client.post('/upload_wav',
                                   data={'file': (BytesIO(wav_data), 'custom_name.wav')})
        
        self.assertEqual(response.status_code, 200)
        
        # Check that file was saved and filename contains timestamp
        files = os.listdir(self.test_upload_dir)
        self.assertEqual(len(files), 1)
        
        # Filename should be in format recording_YYYYMMDD_HHMMSS.wav
        filename = files[0]
        self.assertTrue(filename.startswith('recording_'))
        self.assertTrue(filename.endswith('.wav'))
        # Should have YYYYMMDD format (8 digits after 'recording_')
        timestamp_part = filename[10:18]
        self.assertTrue(timestamp_part.isdigit())
    
    def test_upload_multiple_files_separate(self):
        """Test uploading multiple files creates separate files"""
        import time
        
        wav_data1 = b'RIFFtest WAV data 1'
        wav_data2 = b'RIFFtest WAV data 2'
        
        # Upload first file
        response1 = self.client.post('/upload_wav',
                                    data={'file': (BytesIO(wav_data1), 'test1.wav')})
        self.assertEqual(response1.status_code, 200)
        
        # Wait 1.1 seconds to ensure different timestamps (timestamp is only to second precision)
        time.sleep(1.1)
        
        # Upload second file
        response2 = self.client.post('/upload_wav',
                                    data={'file': (BytesIO(wav_data2), 'test2.wav')})
        self.assertEqual(response2.status_code, 200)
        
        # Check that two separate files exist
        files = os.listdir(self.test_upload_dir)
        self.assertEqual(len(files), 2)
        
        # Files should have different timestamps
        self.assertNotEqual(files[0], files[1])


class TestWavServerConfiguration(unittest.TestCase):
    """Test server configuration and setup"""
    
    def test_app_created(self):
        """Test that Flask app is created correctly"""
        self.assertIsNotNone(app)
        self.assertEqual(app.name, 'wav_server')
    
    def test_upload_dir_created(self):
        """Test that upload directory is created on app init"""
        # The wav_server module creates UPLOAD_DIR on import
        self.assertTrue(os.path.exists(UPLOAD_DIR))
    
    def test_app_configured_with_test_client(self):
        """Test that test client works"""
        app.config['TESTING'] = True
        client = app.test_client()
        self.assertIsNotNone(client)
        
        # Test that test client returns 404 for unknown route
        response = client.get('/unknown_route')
        self.assertEqual(response.status_code, 404)


class TestWavServerIntegration(unittest.TestCase):
    """Integration tests for wav_server.py"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_upload_dir = tempfile.mkdtemp()
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        set_upload_dir(self.test_upload_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_upload_dir, ignore_errors=True)

    def test_full_upload_workflow(self):
        """Test complete upload workflow with various file sizes"""
        # Small file
        small_wav = b'RIFFsmall'
        response = self.client.post('/upload_wav',
                                   data={'file': (BytesIO(small_wav), 'small.wav')})
        self.assertEqual(response.status_code, 200)

        # Medium file
        medium_wav = b'RIFF' + b'medium content' * 100
        response = self.client.post('/upload_wav',
                                   data={'file': (BytesIO(medium_wav), 'medium.wav')})
        self.assertEqual(response.status_code, 200)

        # Large file
        large_wav = b'RIFF' + b'large content' * 10000
        response = self.client.post('/upload_wav',
                                   data={'file': (BytesIO(large_wav), 'large.wav')})
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)
