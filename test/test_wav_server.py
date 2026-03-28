"""Comprehensive tests for wav_server.py Flask application."""
import pytest
import os
import json
import tempfile
import shutil
from io import BytesIO

# Import the app and related functions from wav_server
import wav_server


class TestWavServer:
    """Test suite for WAV server functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down test environment."""
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp()
        self.test_upload_dir = os.path.join(self.test_dir, 'wav_uploads')
        os.makedirs(self.test_upload_dir, exist_ok=True)
        
        # Override default paths for testing
        wav_server.UPLOAD_DIR = self.test_upload_dir
        wav_server.RECORDINGS_INDEX_FILE = os.path.join(
            self.test_upload_dir, 'recordings_index.json'
        )
        
        # Clean up index file
        if os.path.exists(wav_server.RECORDINGS_INDEX_FILE):
            os.remove(wav_server.RECORDINGS_INDEX_FILE)
        
        yield
        
        # Cleanup after tests
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Reset to default paths
        wav_server.UPLOAD_DIR = 'wav_uploads'
        wav_server.RECORDINGS_INDEX_FILE = 'wav_uploads/recordings_index.json'
    
    def create_test_client(self):
        """Create a test client for the Flask app."""
        wav_server.app.config['TESTING'] = True
        return wav_server.app.test_client()
    
    def create_valid_wav_file(self, content=b'DUMMY_WAV_CONTENT'):
        """Create a valid WAV file bytes."""
        # Simple WAV header (44 bytes) + dummy content
        wav_header = (
            b'RIFF' +                      # RIFF header
            (36 + len(content)).to_bytes(4, 'little') +  # File size - 8
            b'WAVE' +                      # WAVE format
            b'fmt ' +                      # fmt chunk
            (16).to_bytes(4, 'little') +  # Chunk size
            (1).to_bytes(2, 'little') +   # Audio format (1 = PCM)
            (1).to_bytes(2, 'little') +   # Number of channels
            (8000).to_bytes(4, 'little') + # Sample rate
            (8000).to_bytes(4, 'little') + # Byte rate
            (1).to_bytes(2, 'little') +   # Block align
            (8).to_bytes(2, 'little') +   # Bits per sample
            b'data' +                      # data chunk
            (len(content)).to_bytes(4, 'little') +  # Chunk size
            content
        )
        return wav_header
    
    # ==================== Upload Tests ====================
    
    def test_upload_wav_missing_file_part(self):
        """Test upload with no file part."""
        client = self.create_test_client()
        response = client.post('/upload_wav')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'No file part' in data['error']
    
    def test_upload_wav_empty_filename(self):
        """Test upload with empty filename/extension."""
        client = self.create_test_client()
        # File with no extension should fail extension check
        response = client.post(
            '/upload_wav',
            data={'file': (BytesIO(b''), 'test')}  # Empty file with no extension
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Invalid file type' in data['error']
    
    def test_upload_wav_invalid_extension(self):
        """Test upload with non-WAV file."""
        client = self.create_test_client()
        response = client.post(
            '/upload_wav',
            data={
                'file': (
                    BytesIO(b'test content'),
                    'test.mp3'
                )
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Invalid file type' in data['error']
        assert '.mp3' in data['error']
    
    def test_upload_wav_missing_riff_header(self):
        """Test upload with file missing RIFF header."""
        client = self.create_test_client()
        response = client.post(
            '/upload_wav',
            data={
                'file': (
                    BytesIO(b'THIS IS NOT A WAV FILE'),
                    'invalid.wav'
                )
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Not a WAV file' in data['error']
    
    def test_upload_wav_missing_wave_format(self):
        """Test upload with file missing WAVE format."""
        client = self.create_test_client()
        # File has RIFF but not WAVE
        bad_header = b'RIFF' + (100).to_bytes(4, 'little') + b'XXXX'
        response = client.post(
            '/upload_wav',
            data={
                'file': (
                    BytesIO(bad_header + b'content'),
                    'invalid.wav'
                )
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Not a WAV file' in data['error']
    
    def test_upload_wav_success(self):
        """Test successful WAV file upload."""
        client = self.create_test_client()
        wav_content = self.create_valid_wav_file(b'test audio data')
        
        response = client.post(
            '/upload_wav',
            data={
                'file': (BytesIO(wav_content), 'test_recording.wav')
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'File uploaded successfully' in data['message']
        assert 'filename' in data
        assert 'size_mb' in data
        assert 'hash' in data
    
    def test_upload_wav_file_too_large(self):
        """Test upload with file exceeding size limit."""
        client = self.create_test_client()
        # Create a file larger than MAX_FILE_SIZE_MB (10MB)
        large_content = self.create_valid_wav_file(b'x' * (11 * 1024 * 1024))
        
        response = client.post(
            '/upload_wav',
            data={
                'file': (BytesIO(large_content), 'large_file.wav')
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'File too large' in data['error']
    
    # ==================== List Recordings Tests ====================
    
    def test_list_recordings_empty(self):
        """Test listing recordings when no files exist."""
        client = self.create_test_client()
        response = client.get('/recordings')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['count'] == 0
        assert data['recordings'] == []
    
    def test_list_recordings_after_upload(self):
        """Test listing recordings after successful upload."""
        client = self.create_test_client()
        wav_content = self.create_valid_wav_file(b'test audio')
        
        # Upload a file
        client.post(
            '/upload_wav',
            data={'file': (BytesIO(wav_content), 'test1.wav')}
        )
        
        # List recordings
        response = client.get('/recordings')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['count'] == 1
        assert len(data['recordings']) == 1
    
    def test_list_recordings_multiple_files(self):
        """Test listing multiple recordings."""
        client = self.create_test_client()
        
        # Upload multiple files
        for i in range(3):
            wav_content = self.create_valid_wav_file(f'test{i}'.encode())
            client.post(
                '/upload_wav',
                data={'file': (BytesIO(wav_content), f'test{i}.wav')}
            )
        
        # List recordings
        response = client.get('/recordings')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 3
        assert len(data['recordings']) == 3
    
    # ==================== Get Recording Tests ====================
    
    def test_get_recording_not_found(self):
        """Test getting a non-existent recording."""
        client = self.create_test_client()
        response = client.get('/recordings/nonexistent.wav')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'not found' in data['error']
    
    def test_get_recording_exists(self):
        """Test getting an existing recording."""
        client = self.create_test_client()
        wav_content = self.create_valid_wav_file(b'test')
        
        # Upload a file
        upload_response = client.post(
            '/upload_wav',
            data={'file': (BytesIO(wav_content), 'test.wav')}
        )
        uploaded_filename = json.loads(upload_response.data)['filename']
        
        # Get the recording
        response = client.get(f'/recordings/{uploaded_filename}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['recording']['filename'] == uploaded_filename
    
    # ==================== Delete Recording Tests ====================
    
    def test_delete_recording_not_found(self):
        """Test deleting a non-existent recording."""
        client = self.create_test_client()
        response = client.delete('/recordings/nonexistent.wav')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'not found' in data['error']
    
    def test_delete_recording_success(self):
        """Test successful deletion of a recording."""
        client = self.create_test_client()
        wav_content = self.create_valid_wav_file(b'test')
        
        # Upload a file
        upload_response = client.post(
            '/upload_wav',
            data={'file': (BytesIO(wav_content), 'test.wav')}
        )
        uploaded_filename = json.loads(upload_response.data)['filename']
        
        # Verify file exists
        assert os.path.exists(os.path.join(self.test_upload_dir, uploaded_filename))
        
        # Delete the recording
        response = client.delete(f'/recordings/{uploaded_filename}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        # Verify file is deleted
        assert not os.path.exists(os.path.join(self.test_upload_dir, uploaded_filename))
        
        # Verify it's removed from list
        list_response = client.get('/recordings')
        list_data = json.loads(list_response.data)
        assert list_data['count'] == 0
    
    # ==================== Health Check Tests ====================
    
    def test_health_check(self):
        """Test health check endpoint."""
        client = self.create_test_client()
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['upload_dir'] == self.test_upload_dir
        assert data['max_file_size_mb'] == 10
    
    # ==================== API Documentation Tests ====================
    
    def test_root_endpoint(self):
        """Test root endpoint with API documentation."""
        client = self.create_test_client()
        response = client.get('/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['service'] == 'WAV Server API'
        assert data['version'] == '1.0.0'
        assert 'endpoints' in data
        assert 'configuration' in data
    
    # ==================== Helper Function Tests ====================
    
    def test_validate_wav_file_valid(self):
        """Test WAV file validation with valid file."""
        wav_content = self.create_valid_wav_file(b'test')
        is_valid, message = wav_server.validate_wav_file(BytesIO(wav_content))
        assert is_valid == True
        assert 'Valid WAV file' in message
    
    def test_validate_wav_file_invalid_header(self):
        """Test WAV file validation with invalid header."""
        is_valid, message = wav_server.validate_wav_file(BytesIO(b'not a wav file'))
        assert is_valid == False
        assert 'Not a WAV file' in message
    
    def test_generate_unique_filename(self):
        """Test unique filename generation."""
        filename = wav_server.generate_unique_filename('My Question.wav')
        # Should contain original name and timestamp, space preserved
        assert 'My Question' in filename
        assert filename.endswith('.wav')
        assert len(filename) > 20  # Should have timestamp
    
    def test_generate_unique_filename_special_chars(self):
        """Test filename generation with special characters."""
        filename = wav_server.generate_unique_filename('Test@#$%^&*.wav')
        # Special chars should be replaced with underscore
        assert '@' not in filename
        assert '#' not in filename
        assert filename.endswith('.wav')
    
    # ==================== Edge Cases ====================
    
    def test_upload_wav_case_insensitive_extension(self):
        """Test that file extension check is case-insensitive."""
        client = self.create_test_client()
        wav_content = self.create_valid_wav_file(b'test')
        
        # Upload with uppercase extension
        response = client.post(
            '/upload_wav',
            data={'file': (BytesIO(wav_content), 'test.WAV')}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_index_json_corruption_recovery(self):
        """Test that corrupted index file is handled gracefully."""
        # Create corrupted index file
        index_path = wav_server.RECORDINGS_INDEX_FILE
        with open(index_path, 'w') as f:
            f.write('not valid json {{{')
        
        # Load should return empty index
        index = wav_server.load_recordings_index()
        assert index == {"recordings": []}
        
        # Cleanup
        os.remove(index_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
