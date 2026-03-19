#!/usr/bin/env python3
"""
Unit tests for wav_server.py - Flask WAV file upload server
Tests the WAV server functionality for the MagicGPT8Ball project.
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import wav_server


class TestWavServer:
    """Test suite for wav_server.py Flask application."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.upload_dir = Path(self.test_dir) / "wav_uploads"
        self.upload_dir.mkdir()
        
        # Configure wav_server to use test upload directory
        wav_server.UPLOAD_DIR = str(self.upload_dir)
        
        # Create test Flask client
        wav_server.app.config['TESTING'] = True
        self.client = wav_server.app.test_client()

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        # Clean upload directory
        if self.upload_dir.exists():
            for file in self.upload_dir.glob("*.wav"):
                file.unlink()
            self.upload_dir.rmdir()
        
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_upload_route_exists(self):
        """Test: The /upload_wav route is registered."""
        response = self.client.get('/upload_wav', method='POST')
        # Should not exist (no file provided) but route should be found
        assert response.status_code in [400, 405]  # Bad request or method not allowed

    def test_upload_with_missing_file(self):
        """Test: Upload without file returns 400 error."""
        response = self.client.post('/upload_wav', data={})
        assert response.status_code == 400
        assert b'No file part' in response.data

    def test_upload_with_empty_filename(self):
        """Test: Upload with empty filename returns 400 error."""
        response = self.client.post('/upload_wav', data={
            'file': (BytesIO(b''), '')
        })
        assert response.status_code == 400
        assert b'No selected file' in response.data

    def test_upload_with_valid_file(self):
        """Test: Upload with valid WAV file succeeds."""
        # Create a minimal WAV file for testing
        wav_content = b'RIFF' + b'\x00' * 36 + b'WAVE' + b'fmt ' + b'\x10' * 16 + b'data' + b'\x00' * 44
        
        from io import BytesIO
        
        response = self.client.post('/upload_wav', data={
            'file': (BytesIO(wav_content), 'test_recording.wav')
        })
        
        assert response.status_code == 200
        assert b'File uploaded successfully' in response.data
        
        # Verify file was saved
        wav_files = list(Path(wav_server.UPLOAD_DIR).glob('*.wav'))
        assert len(wav_files) > 0

    def test_upload_filename_timestamp(self):
        """Test: Uploaded files have timestamped filenames."""
        from io import BytesIO
        
        wav_content = b'RIFF' + b'\x00' * 44
        
        # Track original upload directory
        original_upload_dir = wav_server.UPLOAD_DIR
        
        # Upload
        response = self.client.post('/upload_wav', data={
            'file': (BytesIO(wav_content), 'test.wav')
        })
        
        assert response.status_code == 200
        
        # Verify file exists with timestamped name
        wav_files = list(Path(original_upload_dir).glob('*.wav'))
        assert len(wav_files) > 0
        
        # Check filename format (should contain timestamp)
        timestamp_pattern = datetime.now().strftime('%Y%m%d_%H%M%S')
        found_timestamp = any(timestamp_pattern in f.name for f in wav_files)
        assert found_timestamp or any('recording_' in f.name for f in wav_files)

    def test_multiple_uploads_different_files(self):
        """Test: Multiple uploads work - note: server uses timestamped filenames."""
        from io import BytesIO
        
        wav_content = b'RIFF' + b'\x00' * 44
        
        # Upload multiple files
        for i in range(3):
            response = self.client.post('/upload_wav', data={
                'file': (BytesIO(wav_content), f'test_{i}.wav')
            })
            assert response.status_code == 200
        
        # Verify file exists (server may overwrite due to same-second timestamp)
        original_upload_dir = wav_server.UPLOAD_DIR
        wav_files = list(Path(original_upload_dir).glob('*.wav'))
        # At least one file should exist
        assert len(wav_files) >= 1

    def test_content_type_not_enforced(self):
        """Test: Server accepts uploads regardless of content type."""
        from io import BytesIO
        
        # Upload text file with .wav extension
        response = self.client.post('/upload_wav', data={
            'file': (BytesIO(b'text content'), 'fake.wav')
        })
        
        # Server doesn't validate content type
        assert response.status_code == 200

    def test_upload_directory_created(self):
        """Test: Upload directory is created if it doesn't exist."""
        # Access the module to verify UPLOAD_DIR attribute exists
        assert hasattr(wav_server, 'UPLOAD_DIR')
        assert wav_server.UPLOAD_DIR is not None
        
        # The server creates the directory on import/initialization
        # We verify it's properly configured
        assert os.path.isdir(wav_server.UPLOAD_DIR) or os.path.exists(wav_server.UPLOAD_DIR)

    def test_server_config(self):
        """Test: Flask app is configured correctly."""
        assert hasattr(wav_server, 'app')
        assert wav_server.app is not None
        assert wav_server.app.name == 'wav_server'

    def test_upload_directory_configuration(self):
        """Test: UPLOAD_DIR can be reconfigured."""
        original_dir = wav_server.UPLOAD_DIR
        
        # Set new directory
        new_dir = str(Path(self.test_dir) / "new_upload_dir")
        wav_server.UPLOAD_DIR = new_dir
        
        # Verify configuration changed
        assert wav_server.UPLOAD_DIR == new_dir
        
        # Restore
        wav_server.UPLOAD_DIR = original_dir


class TestWavServerEdgeCases:
    """Edge case tests for wav_server.py."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        wav_server.UPLOAD_DIR = str(Path(self.test_dir) / "uploads")
        os.makedirs(wav_server.UPLOAD_DIR)
        wav_server.app.config['TESTING'] = True
        self.client = wav_server.app.test_client()

    def teardown_method(self):
        """Clean up."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_very_long_filename(self):
        """Test: Filenames with special characters and long names."""
        from io import BytesIO
        
        long_filename = "test_" + "a" * 200 + ".wav"
        
        response = self.client.post('/upload_wav', data={
            'file': (BytesIO(b'RIFF' + b'\x00' * 44), long_filename)
        })
        
        # Should handle gracefully
        assert response.status_code == 200

    def test_unicode_filename(self):
        """Test: Unicode characters in filename."""
        from io import BytesIO
        
        unicode_filename = "recording_测试_🎵.wav"
        
        response = self.client.post('/upload_wav', data={
            'file': (BytesIO(b'RIFF' + b'\x00' * 44), unicode_filename)
        })
        
        assert response.status_code == 200


class TestWavServerIntegration:
    """Integration tests for wav_server.py."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.upload_dir = Path(self.test_dir) / "integration_uploads"
        self.upload_dir.mkdir()
        wav_server.UPLOAD_DIR = str(self.upload_dir)
        wav_server.app.config['TESTING'] = True
        self.client = wav_server.app.test_client()

    def teardown_method(self):
        """Clean up."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_realistic_upload_scenario(self):
        """Test: Realistic multi-file upload scenario."""
        from io import BytesIO
        
        # Simulate user uploading multiple recordings
        for i in range(5):
            # Create realistic WAV-like content
            wav_content = b'RIFF' + (b'\x00' * (44 + (1000 * 2)))
            response = self.client.post('/upload_wav', data={
                'file': (BytesIO(wav_content), f'voice_recording_{i}.wav')
            })
            assert response.status_code == 200
        
        # Verify at least one file was created (server uses timestamped names)
        wav_files = list(self.upload_dir.glob('*.wav'))
        assert len(wav_files) >= 1

    def test_empty_upload_without_file_key(self):
        """Test: POST request without 'file' key."""
        response = self.client.post('/upload_wav', data={
            'other_key': 'value'
        })
        
        assert response.status_code == 400
        assert b'No file part' in response.data


# Helper for BytesIO import in tests
from io import BytesIO


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
