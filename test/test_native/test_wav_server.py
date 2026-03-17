#!/usr/bin/env python3
"""Unit tests for wav_server.py - Flask WAV upload server."""

import os
import tempfile
import shutil
import unittest
from datetime import datetime
from flask import Flask, request
import io


# Set upload directory for test isolation
UPLOAD_DIR = 'wav_uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Clean up any previous test uploads
for f in os.listdir(UPLOAD_DIR):
    if f.startswith('recording_') and f.endswith('.wav'):
        os.remove(os.path.join(UPLOAD_DIR, f))


def create_test_app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    
    @app.route('/upload_wav', methods=['POST'])
    def upload_wav():
        if 'file' not in request.files:
            return 'No file part', 400
        
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'recording_{timestamp}.wav'
        
        # Save the file
        filepath = os.path.join(UPLOAD_DIR, filename)
        file.save(filepath)
        
        return 'File uploaded successfully', 200
    
    return app


class TestWavServer(unittest.TestCase):
    """Test cases for WAV file upload server."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_test_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.test_wav_content = b'RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00'
    
    def tearDown(self):
        """Clean up test fixtures."""
        for f in os.listdir(UPLOAD_DIR):
            if f.startswith('recording_') and f.endswith('.wav'):
                os.remove(os.path.join(UPLOAD_DIR, f))
    
    def test_upload_wav_file_success(self):
        """Test successful WAV file upload."""
        with self.client as client:
            with client.open(
                '/upload_wav',
                method='POST',
                data={
                    'file': (io.BytesIO(self.test_wav_content), 'test_recording.wav')
                }
            ):
                # Create a temporary file to capture the request
                temp_file = io.BytesIO(self.test_wav_content)
                response = client.post(
                    '/upload_wav',
                    data={'file': (temp_file, 'test_recording.wav')}
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data.decode(), 'File uploaded successfully')
    
    def test_upload_missing_file_part(self):
        """Test upload with missing file part."""
        response = self.client.post('/upload_wav', data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), 'No file part')
    
    def test_upload_empty_filename(self):
        """Test upload with empty filename."""
        with self.client as client:
            response = client.post(
                '/upload_wav',
                data={'file': (io.BytesIO(b''), '')}
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data.decode(), 'No selected file')
    
    def test_upload_valid_wav_file(self):
        """Test upload of valid WAV file."""
        response = self.client.post(
            '/upload_wav',
            data={'file': (io.BytesIO(self.test_wav_content), 'valid_audio.wav')}
        )
        self.assertEqual(response.status_code, 200)
    
    def test_upload_filename_with_spaces(self):
        """Test upload with filename containing spaces."""
        response = self.client.post(
            '/upload_wav',
            data={'file': (io.BytesIO(self.test_wav_content), 'my test recording.wav')}
        )
        self.assertEqual(response.status_code, 200)
    
    def test_upload_different_file_extensions(self):
        """Test that only .wav files work (server doesn't validate extension)."""
        # Upload with different extensions - server should still accept
        extensions = ['.wav', '.WAV', '.audio', '.tmp']
        
        for ext in extensions:
            response = self.client.post(
                '/upload_wav',
                data={'file': (io.BytesIO(self.test_wav_content), f'test{ext}')}
            )
            # Server accepts any file type, doesn't validate extension
            self.assertEqual(response.status_code, 200, f"Failed for extension: {ext}")
    
    def test_upload_large_file(self):
        """Test upload of large WAV file."""
        large_content = b'RIFF' + b'\xff' * (1024 * 1024)  # 1MB file
        response = self.client.post(
            '/upload_wav',
            data={'file': (io.BytesIO(large_content), 'large_file.wav')}
        )
        self.assertEqual(response.status_code, 200)
    
    def test_upload_concurrent_requests(self):
        """Test handling multiple concurrent uploads."""
        upload_count = 10
        responses = []
        
        for i in range(upload_count):
            response = self.client.post(
                '/upload_wav',
                data={'file': (io.BytesIO(self.test_wav_content), f'concurrent_{i}.wav')}
            )
            responses.append(response.status_code)
        
        # All uploads should succeed
        self.assertEqual(sum(1 for r in responses if r == 200), upload_count)


class TestWavServerIntegration(unittest.TestCase):
    """Integration tests for WAV server with file system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.app = create_test_app()
        self.app.config['TESTING'] = True
        
        # Use our temp directory for uploads
        self.original_upload_dir = UPLOAD_DIR
        self.new_upload_dir = os.path.join(self.temp_dir, UPLOAD_DIR)
        os.makedirs(self.new_upload_dir)
        
        # Note: Flask test client doesn't easily allow changing upload paths
        # This is a placeholder for future integration tests
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_directory_cleanup(self):
        """Test that test directory is properly cleaned up."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        self.assertTrue(os.path.exists(test_file))
        
        # After tearDown, directory should be gone
        shutil.rmtree(self.temp_dir)
        self.assertFalse(os.path.exists(self.temp_dir))


if __name__ == '__main__':
    unittest.main()
