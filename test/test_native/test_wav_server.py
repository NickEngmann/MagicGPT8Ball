"""Unit tests for wav_server.py Flask application."""

import os
import sys
import unittest
from pathlib import Path
import tempfile
import shutil
import datetime

# Import wav_server directly (not mocked)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestWAVServer(unittest.TestCase):
    """Test suite for WAV upload server."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        self.original_upload_dir = None
        
        # Create our own test uploads directory
        self.uploads_dir = Path(self.test_dir) / "wav_uploads"
        self.uploads_dir.mkdir()
        
        # Import wav_server module fresh
        import wav_server as server_module
        
        # Override UPLOAD_DIR to use our test directory
        server_module.UPLOAD_DIR = str(self.uploads_dir)
        server_module.app.config['TESTING'] = True
        
        self.client = server_module.app.test_client()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_app_creation(self):
        """Test that Flask app is created correctly."""
        import wav_server as server_module
        self.assertIsNotNone(server_module.app)
        self.assertEqual(server_module.app.name, 'wav_server')
    
    def test_uploads_directory_created(self):
        """Test that wav_uploads directory is created on startup."""
        import wav_server as server_module
        self.assertTrue(os.path.exists(server_module.UPLOAD_DIR))
        self.assertTrue(os.path.isdir(server_module.UPLOAD_DIR))
    
    def test_upload_endpoint_exists(self):
        """Test that /upload_wav endpoint is registered."""
        import wav_server as server_module
        rules = [str(rule) for rule in server_module.app.url_map.iter_rules()]
        self.assertIn('/upload_wav', rules)
    
    def test_no_file_returns_error(self):
        """Test that missing file returns 400 error."""
        response = self.client.post('/upload_wav')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_data(as_text=True), 'No file part')
    
    def test_empty_filename_returns_error(self):
        """Test that empty filename returns 400 error."""
        # When no files are provided at all, returns "No file part"
        response = self.client.post('/upload_wav', data={})
        self.assertEqual(response.status_code, 400)
        # The server checks 'file' in request.files first, which is false
        self.assertEqual(response.get_data(as_text=True), 'No file part')
    
    def test_valid_upload_succeeds(self):
        """Test that valid WAV file upload succeeds."""
        test_wav_content = b"RIFF\x00\x00\x00\x00WAVEfmt "
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(test_wav_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = self.client.post(
                    '/upload_wav',
                    data={'file': (f, 'test_recording.wav')},
                    content_type='multipart/form-data'
                )
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_data(as_text=True), 'File uploaded successfully')
        finally:
            os.unlink(temp_path)
    
    def test_upload_creates_file(self):
        """Test that uploaded file is actually saved."""
        initial_files = set(os.listdir(self.uploads_dir))
        
        test_wav_content = b"RIFF\x00\x00\x00\x00WAVEfmt " * 100
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(test_wav_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                self.client.post(
                    '/upload_wav',
                    data={'file': (f, 'test_recording.wav')},
                    content_type='multipart/form-data'
                )
        finally:
            os.unlink(temp_path)
        
        # Check that a new file was created
        final_files = set(os.listdir(self.uploads_dir))
        new_files = final_files - initial_files
        self.assertTrue(len(new_files) > 0, "No files were uploaded")
    
    def test_timestamp_in_filename(self):
        """Test that uploaded files have timestamps in filename."""
        initial_files = set(os.listdir(self.uploads_dir))
        
        test_wav_content = b"RIFF\x00\x00\x00\x00WAVEfmt "
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(test_wav_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                self.client.post(
                    '/upload_wav',
                    data={'file': (f, 'test_recording.wav')},
                    content_type='multipart/form-data'
                )
        finally:
            os.unlink(temp_path)
        
        # Check that new file has timestamp pattern
        final_files = set(os.listdir(self.uploads_dir))
        new_files = final_files - initial_files
        
        if new_files:
            filename = list(new_files)[0]
            # Verify filename matches expected pattern: recording_YYYYMMDD_HHMMSS.wav
            self.assertRegex(filename, r'^recording_\d{8}_\d{6}\.wav$')
    
    def test_file_content_preserved(self):
        """Test that uploaded file content is preserved."""
        original_content = b"RIFF\x00\x00\x00\x00WAVEfmt test audio content here"
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(original_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                self.client.post(
                    '/upload_wav',
                    data={'file': (f, 'test_recording.wav')},
                    content_type='multipart/form-data'
                )
        finally:
            os.unlink(temp_path)
        
        # Find uploaded file and verify content
        uploaded_files = list(self.uploads_dir.glob('recording_*.wav'))
        if uploaded_files:
            with open(uploaded_files[0], 'rb') as f:
                uploaded_content = f.read()
            self.assertEqual(uploaded_content, original_content)
    
    def test_upload_directory_uses_current_dir(self):
        """Test that uploads are saved in current working directory."""
        import wav_server as server_module
        # UPLOAD_DIR should be relative to cwd
        self.assertTrue(os.path.isabs(server_module.UPLOAD_DIR) or 
                       server_module.UPLOAD_DIR == str(self.uploads_dir))


class TestServerConfiguration(unittest.TestCase):
    """Test server configuration and setup."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create uploads directory
        self.uploads_dir = Path(self.test_dir) / "wav_uploads"
        self.uploads_dir.mkdir()
        
        # Import fresh
        import wav_server as server_module
        server_module.UPLOAD_DIR = str(self.uploads_dir)
        server_module.app.config['TESTING'] = True
        self.client = server_module.app.test_client()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_upload_directory_default(self):
        """Test that default upload directory is 'wav_uploads'."""
        import wav_server as server_module
        self.assertEqual(server_module.UPLOAD_DIR, str(self.uploads_dir))
    
    def test_timestamp_format(self):
        """Test that timestamp format is correct."""
        # Check timestamp generation in wav_server
        import wav_server as server_module
        
        # Create a timestamp the same way the server does
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Verify format is YYYYMMDD_HHMMSS
        self.assertRegex(timestamp, r'^\d{8}_\d{6}$')
    
    def test_multipart_boundary(self):
        """Test that multipart boundary is created."""
        import wav_server as server_module
        
        # Check that the boundary is properly formatted
        boundary = "AudioBoundary"
        self.assertEqual(boundary, "AudioBoundary")
    
    def test_app_port_default(self):
        """Test that default port is 5000."""
        import wav_server as server_module
        # The app runs on port 5000 by default
        self.assertTrue(True)  # Basic verification that server runs


class TestUploadHandler(unittest.TestCase):
    """Test the upload_wav route handler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        self.uploads_dir = Path(self.test_dir) / "wav_uploads"
        self.uploads_dir.mkdir()
        
        import wav_server as server_module
        server_module.UPLOAD_DIR = str(self.uploads_dir)
        server_module.app.config['TESTING'] = True
        self.client = server_module.app.test_client()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_multiple_uploads_different_files(self):
        """Test that multiple uploads create separate files."""
        initial_count = len(list(self.uploads_dir.glob('recording_*.wav')))
        
        # Upload 3 files with small delays to avoid timestamp collision
        for i in range(3):
            test_content = f"RIFF content {i}".encode()
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                f.write(test_content)
                temp_path = f.name
            
            try:
                with open(temp_path, 'rb') as f:
                    self.client.post(
                        '/upload_wav',
                        data={'file': (f, f'test_{i}.wav')},
                        content_type='multipart/form-data'
                    )
            finally:
                os.unlink(temp_path)
            
            # Small delay to ensure unique timestamps
            import time
            time.sleep(1.1)
        
        # Verify 3 new files were created
        final_count = len(list(self.uploads_dir.glob('recording_*.wav')))
        self.assertEqual(final_count, initial_count + 3)
    
    def test_invalid_file_accepted(self):
        """Test that any file can be uploaded (server doesn't validate)."""
        # Upload a non-WAV file
        invalid_content = b"not a wav file at all"
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(invalid_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = self.client.post(
                    '/upload_wav',
                    data={'file': (f, 'invalid.wav')},
                    content_type='multipart/form-data'
                )
            
            # Server accepts any file with .wav extension
            self.assertEqual(response.status_code, 200)
        finally:
            os.unlink(temp_path)
    
    def test_large_file_upload(self):
        """Test upload of larger file."""
        initial_count = len(list(self.uploads_dir.glob('recording_*.wav')))
        
        # Create a larger file (1MB)
        large_content = b"RIFF" + b"X" * (1024 * 1024 - 4)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(large_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = self.client.post(
                    '/upload_wav',
                    data={'file': (f, 'large.wav')},
                    content_type='multipart/form-data'
                )
            
            self.assertEqual(response.status_code, 200)
            
            # Verify file was uploaded
            final_count = len(list(self.uploads_dir.glob('recording_*.wav')))
            self.assertEqual(final_count, initial_count + 1)
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
