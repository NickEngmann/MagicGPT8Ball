"""
Test suite for wav_server.py - WAV file upload server

Tests cover:
- WAV header validation
- File upload handling
- Error handling
- Batch uploads
- Cleanup operations
"""

import os
import sys
import struct
import tempfile
import shutil
import pytest
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wav_server import (
    app,
    validate_wav_header,
    generate_checksum,
    cleanup_old_uploads,
    UPLOAD_DIR,
    MAX_FILE_SIZE
)


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory."""
    original_dir = UPLOAD_DIR
    temp_dir = tempfile.mkdtemp(prefix='wav_test_')
    
    # Update the module variable
    import wav_server
    wav_server.UPLOAD_DIR = temp_dir
    os.makedirs(temp_dir, exist_ok=True)
    
    yield temp_dir
    
    # Cleanup
    wav_server.UPLOAD_DIR = original_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_wav_file():
    """Create a sample WAV file for testing."""
    temp_dir = tempfile.mkdtemp()
    wav_path = os.path.join(temp_dir, 'sample.wav')
    
    # Create a minimal valid WAV file (44-byte header only, no audio data)
    with open(wav_path, 'wb') as f:
        # RIFF header
        f.write(b'RIFF')
        # File size (40 bytes for header only)
        f.write(struct.pack('<I', 40))
        # WAV signature
        f.write(b'WAVE')
        # fmt chunk
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))  # Chunk size
        f.write(struct.pack('<H', 1))   # Audio format (PCM)
        f.write(struct.pack('<H', 1))   # Number of channels
        f.write(struct.pack('<I', 16000))  # Sample rate
        f.write(struct.pack('<I', 32000))  # Byte rate
        f.write(struct.pack('<H', 2))   # Block align
        f.write(struct.pack('<H', 16))  # Bits per sample
        # data chunk
        f.write(b'data')
        f.write(struct.pack('<I', 0))   # Data size (empty)
    
    yield wav_path
    
    os.unlink(wav_path)
    os.rmdir(temp_dir)


@pytest.fixture
def sample_wav_file_with_data():
    """Create a sample WAV file with actual audio data."""
    temp_dir = tempfile.mkdtemp()
    wav_path = os.path.join(temp_dir, 'sample_with_data.wav')

    # Create a WAV file with some audio data
    num_samples = 1000
    sample_rate = 16000
    bits_per_sample = 16
    num_channels = 1

    data_size = num_samples * num_channels * bits_per_sample // 8
    
    with open(wav_path, 'wb') as f:
        # RIFF header (4 + 4 bytes)
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))  # Total file size - 8
        
        # WAV signature (4 bytes)
        f.write(b'WAVE')
        
        # fmt chunk (24 bytes total)
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))  # Chunk size
        f.write(struct.pack('<H', 1))   # Audio format (PCM)
        f.write(struct.pack('<H', num_channels))  # Number of channels
        f.write(struct.pack('<I', sample_rate))  # Sample rate
        byte_rate = sample_rate * num_channels * bits_per_sample // 8
        f.write(struct.pack('<I', byte_rate))  # Byte rate
        f.write(struct.pack('<H', num_channels * bits_per_sample // 8))  # Block align
        f.write(struct.pack('<H', bits_per_sample))  # Bits per sample
        
        # data chunk header (8 bytes) + data
        f.write(b'data')
        f.write(struct.pack('<I', data_size))  # Data size
        f.write(b'\x00' * data_size)  # Audio data (silence)

    yield wav_path

    os.unlink(wav_path)
    os.rmdir(temp_dir)


class TestWAVHeaderValidation:
    """Tests for validate_wav_header function."""
    
    def test_valid_wav_file(self, sample_wav_file_with_data):
        """Test validation of a valid WAV file."""
        result = validate_wav_header(sample_wav_file_with_data)
        
        assert result['valid'] is True
        assert result['sample_rate'] == 16000
        assert result['num_channels'] == 1
        assert result['bits_per_sample'] == 16
        assert result['duration_seconds'] > 0
        assert 'error' not in result
    
    def test_empty_file(self):
        """Test validation of an empty file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        
        result = validate_wav_header(temp_file.name)
        
        assert result['valid'] is False
        assert 'too small' in result['error'].lower()
        
        os.unlink(temp_file.name)
    
    def test_invalid_file(self):
        """Test validation of a non-WAV file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_file.write(b'This is not a WAV file')
        temp_file.close()
        
        result = validate_wav_header(temp_file.name)
        
        assert result['valid'] is False
        
        os.unlink(temp_file.name)
    
    def test_file_too_small(self):
        """Test validation of a file smaller than 44 bytes."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(b'RIFF' + b'\x00' * 10)
        temp_file.close()
        
        result = validate_wav_header(temp_file.name)
        
        assert result['valid'] is False
        assert 'too small' in result['error'].lower()
        
        os.unlink(temp_file.name)
    
    def test_missing_wav_signature(self):
        """Test file with RIFF but no WAV signature."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_file.write(b'RIFF' + b'\x00' * 40 + b'NOTWAVE')
        temp_file.close()
        
        result = validate_wav_header(temp_file.name)
        
        assert result['valid'] is False
        assert 'wav signature' in result['error'].lower()
        
        os.unlink(temp_file.name)


class TestChecksumGeneration:
    """Tests for generate_checksum function."""
    
    def test_consistent_checksum(self):
        """Test that checksum is consistent for same file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(b'test content')
        temp_file.close()
        
        checksum1 = generate_checksum(temp_file.name)
        checksum2 = generate_checksum(temp_file.name)
        
        assert checksum1 == checksum2
        assert len(checksum1) == 32  # MD5 produces 32 hex characters
        
        os.unlink(temp_file.name)
    
    def test_different_files_different_checksums(self):
        """Test that different files produce different checksums."""
        temp_file1 = tempfile.NamedTemporaryFile(delete=False)
        temp_file1.write(b'content 1')
        temp_file1.close()
        
        temp_file2 = tempfile.NamedTemporaryFile(delete=False)
        temp_file2.write(b'content 2')
        temp_file2.close()
        
        checksum1 = generate_checksum(temp_file1.name)
        checksum2 = generate_checksum(temp_file2.name)
        
        assert checksum1 != checksum2
        
        os.unlink(temp_file1.name)
        os.unlink(temp_file2.name)


class TestWAVUploadEndpoint:
    """Tests for the upload_wav endpoint."""
    
    def test_successful_upload(self, client, temp_upload_dir, sample_wav_file_with_data):
        """Test successful WAV file upload."""
        with open(sample_wav_file_with_data, 'rb') as f:
            response = client.post('/upload_wav', 
                                   data={'file': (f, 'test.wav')},
                                   content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'filename' in data
        assert 'checksum' in data
        assert 'metadata' in data
        assert 'sample_rate' in data['metadata']
    
    def test_upload_without_file(self, client):
        """Test upload without file part."""
        response = client.post('/upload_wav', data={})
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'file part' in data['error'].lower()
    
    def test_upload_empty_filename(self, client):
        """Test upload with empty filename."""
        # Create a minimal valid WAV file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        num_samples = 100
        data_size = num_samples * 1 * 16 // 8
        sample_rate = 16000
        
        with open(temp_file.name, 'wb') as f:
            f.write(b'RIFF')
            f.write(struct.pack('<I', 36 + data_size))
            f.write(b'WAVE')
            f.write(b'fmt ')
            f.write(struct.pack('<I', 16))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<I', sample_rate))
            byte_rate = sample_rate * 1 * 16 // 8
            f.write(struct.pack('<I', byte_rate))
            f.write(struct.pack('<H', 2))
            f.write(struct.pack('<H', 16))
            f.write(b'data')
            f.write(struct.pack('<I', data_size))
            f.write(b'\x00' * data_size)
        
        # Test with empty filename
        with open(temp_file.name, 'rb') as f:
            response = client.post('/upload_wav',
                                   data={'file': (f, '')},  # Empty filename
                                   content_type='multipart/form-data')

        assert response.status_code == 400
        data = response.get_json()

        assert data['success'] is False
        assert 'selected file' in data['error'].lower()
        
        os.unlink(temp_file.name)
    
    def test_upload_non_wav_file(self, client):
        """Test upload of non-WAV file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        temp_file.write(b'test content')
        temp_file.close()
        
        with open(temp_file.name, 'rb') as f:
            response = client.post('/upload_wav', 
                                   data={'file': (f, 'test.txt')},
                                   content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'wav' in data['error'].lower()
        
        os.unlink(temp_file.name)
    
    def test_upload_too_large_file(self, client):
        """Test upload of file larger than max size."""
        # Create a file larger than MAX_FILE_SIZE
        large_content = b'x' * (MAX_FILE_SIZE + 1)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_file.write(large_content)
        temp_file.close()
        
        with open(temp_file.name, 'rb') as f:
            response = client.post('/upload_wav', 
                                   data={'file': (f, 'large.wav')},
                                   content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        
        os.unlink(temp_file.name)
    
    def test_upload_invalid_wav(self, client):
        """Test upload of file with .wav extension but invalid content."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_file.write(b'Not a valid WAV file at all')
        temp_file.close()
        
        with open(temp_file.name, 'rb') as f:
            response = client.post('/upload_wav', 
                                   data={'file': (f, 'invalid.wav')},
                                   content_type='multipart/form-data')
        
        # Should reject invalid WAV file
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        
        os.unlink(temp_file.name)


class TestBatchUploadEndpoint:
    """Tests for the upload_wav_batch endpoint."""

    def test_batch_upload_success(self, client, temp_upload_dir):
        """Test successful batch upload."""
        # Create test files directly in the upload directory
        file_handles = []
        for i in range(3):
            test_file = os.path.join(temp_upload_dir, f'batch_file_{i}.wav')
            num_samples = 100
            data_size = num_samples * 1 * 16 // 8
            sample_rate = 16000
            
            with open(test_file, 'wb') as f:
                f.write(b'RIFF')
                f.write(struct.pack('<I', 36 + data_size))
                f.write(b'WAVE')
                f.write(b'fmt ')
                f.write(struct.pack('<I', 16))
                f.write(struct.pack('<H', 1))
                f.write(struct.pack('<H', 1))
                f.write(struct.pack('<I', sample_rate))
                byte_rate = sample_rate * 1 * 16 // 8
                f.write(struct.pack('<I', byte_rate))
                f.write(struct.pack('<H', 2))
                f.write(struct.pack('<H', 16))
                f.write(b'data')
                f.write(struct.pack('<I', data_size))
                f.write(b'\x00' * data_size)
            
            file_handles.append(open(test_file, 'rb'))
        
        # Create multipart form data with multiple files
        form_data = {
            'files': [(f, f'batch_file_{i}.wav') for i, f in enumerate(file_handles)]
        }
        
        response = client.post('/upload_wav_batch', data=form_data)
        
        # Files were small but valid WAV files, so all succeeded
        assert response.status_code == 200  # All files valid
        data = response.get_json()

        assert 'uploaded' in data
        assert 'failed' in data
        assert 'files' in data
        assert data['uploaded'] >= 0
        assert data['failed'] >= 0

        # Cleanup
        for f in file_handles:
            f.close()
    
    def test_batch_upload_empty(self, client):
        """Test batch upload with no files."""
        response = client.post('/upload_wav_batch')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False


class TestHealthEndpoint:
    """Tests for the /health endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'upload_directory' in data
        assert 'max_file_size_mb' in data


class TestListUploadsEndpoint:
    """Tests for the /uploads endpoint."""
    
    def test_list_uploads_empty(self, client, temp_upload_dir):
        """Test listing uploads when directory is empty."""
        response = client.get('/uploads')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['uploads'] == []
        assert data['total'] == 0
    
    def test_list_uploads_with_files(self, client, temp_upload_dir):
        """Test listing uploads with files present."""
        # Create some test files directly in temp_upload_dir
        for i in range(3):
            test_file = os.path.join(temp_upload_dir, f'test_{i}.wav')
            num_samples = 100
            data_size = num_samples * 1 * 16 // 8
            sample_rate = 16000
            
            with open(test_file, 'wb') as f:
                f.write(b'RIFF')
                f.write(struct.pack('<I', 36 + data_size))
                f.write(b'WAVE')
                f.write(b'fmt ')
                f.write(struct.pack('<I', 16))
                f.write(struct.pack('<H', 1))
                f.write(struct.pack('<H', 1))
                f.write(struct.pack('<I', sample_rate))
                byte_rate = sample_rate * 1 * 16 // 8
                f.write(struct.pack('<I', byte_rate))
                f.write(struct.pack('<H', 2))
                f.write(struct.pack('<H', 16))
                f.write(b'data')
                f.write(struct.pack('<I', data_size))
                f.write(b'\x00' * data_size)

        response = client.get('/uploads')

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert len(data['uploads']) == 3
    
    def test_list_uploads_with_pagination(self, client, temp_upload_dir):
        """Test listing uploads with pagination."""
        # Create 5 test files with proper WAV structure
        for i in range(5):
            test_file = os.path.join(temp_upload_dir, f'test_{i}.wav')
            num_samples = 100
            data_size = num_samples * 1 * 16 // 8
            sample_rate = 16000
            
            with open(test_file, 'wb') as f:
                f.write(b'RIFF')
                f.write(struct.pack('<I', 36 + data_size))
                f.write(b'WAVE')
                f.write(b'fmt ')
                f.write(struct.pack('<I', 16))
                f.write(struct.pack('<H', 1))
                f.write(struct.pack('<H', 1))
                f.write(struct.pack('<I', sample_rate))
                byte_rate = sample_rate * 1 * 16 // 8
                f.write(struct.pack('<I', byte_rate))
                f.write(struct.pack('<H', 2))
                f.write(struct.pack('<H', 16))
                f.write(b'data')
                f.write(struct.pack('<I', data_size))
                f.write(b'\x00' * data_size)

        # Test with offset and limit
        response = client.get('/uploads?limit=2&offset=1')

        assert response.status_code == 200
        data = response.get_json()

        assert len(data['uploads']) == 2
        assert data['limit'] == 2
        assert data['offset'] == 1


class TestDeleteEndpoint:
    """Tests for the delete upload endpoint."""

    def test_delete_existing_file(self, client, temp_upload_dir):
        """Test deleting an existing file."""
        # Create a test file with valid WAV structure
        test_file = os.path.join(temp_upload_dir, 'test_delete.wav')
        num_samples = 100
        data_size = num_samples * 1 * 16 // 8
        sample_rate = 16000
        
        with open(test_file, 'wb') as f:
            f.write(b'RIFF')
            f.write(struct.pack('<I', 36 + data_size))
            f.write(b'WAVE')
            f.write(b'fmt ')
            f.write(struct.pack('<I', 16))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<I', sample_rate))
            byte_rate = sample_rate * 1 * 16 // 8
            f.write(struct.pack('<I', byte_rate))
            f.write(struct.pack('<H', 2))
            f.write(struct.pack('<H', 16))
            f.write(b'data')
            f.write(struct.pack('<I', data_size))
            f.write(b'\x00' * data_size)

        response = client.delete(f'/uploads/delete/test_delete.wav')

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert not os.path.exists(test_file)
    
    def test_delete_nonexistent_file(self, client, temp_upload_dir):
        """Test deleting a non-existent file."""
        response = client.delete('/uploads/delete/nonexistent.wav')
        
        assert response.status_code == 404
        data = response.get_json()
        
        assert data['success'] is False
        assert 'not found' in data['error'].lower()


class TestCleanupEndpoint:
    """Tests for the cleanup endpoint."""
    
    def test_cleanup_empty(self, client):
        """Test cleanup when directory is empty."""
        response = client.post('/cleanup')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['deleted_count'] == 0
    
    def test_cleanup_with_old_files(self, temp_upload_dir):
        """Test cleanup removing old files."""
        # Create files with old modification time
        old_time = datetime.now().timestamp() - (48 * 3600)  # 48 hours ago

        for i in range(3):
            filepath = os.path.join(temp_upload_dir, f'old_file_{i}.wav')
            num_samples = 100
            data_size = num_samples * 1 * 16 // 8
            sample_rate = 16000
            
            with open(filepath, 'wb') as f:
                f.write(b'RIFF')
                f.write(struct.pack('<I', 36 + data_size))
                f.write(b'WAVE')
                f.write(b'fmt ')
                f.write(struct.pack('<I', 16))
                f.write(struct.pack('<H', 1))
                f.write(struct.pack('<H', 1))
                f.write(struct.pack('<I', sample_rate))
                byte_rate = sample_rate * 1 * 16 // 8
                f.write(struct.pack('<I', byte_rate))
                f.write(struct.pack('<H', 2))
                f.write(struct.pack('<H', 16))
                f.write(b'data')
                f.write(struct.pack('<I', data_size))
                f.write(b'\x00' * data_size)
            os.utime(filepath, (old_time, old_time))

        # Run cleanup (default 24 hours)
        deleted = cleanup_old_uploads(max_age_hours=24)

        assert deleted == 3


class TestIntegration:
    """Integration tests for the server."""

    def test_full_upload_workflow(self, client, temp_upload_dir):
        """Test complete upload workflow."""
        # Create a valid WAV file
        sample_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        num_samples = 1000
        sample_rate = 16000
        bits_per_sample = 16
        num_channels = 1
        data_size = num_samples * num_channels * bits_per_sample // 8

        sample_file.write(b'RIFF')
        sample_file.write(struct.pack('<I', 36 + data_size))
        sample_file.write(b'WAVE')
        sample_file.write(b'fmt ')
        sample_file.write(struct.pack('<I', 16))
        sample_file.write(struct.pack('<H', 1))
        sample_file.write(struct.pack('<H', num_channels))
        sample_file.write(struct.pack('<I', sample_rate))
        byte_rate = sample_rate * num_channels * bits_per_sample // 8
        sample_file.write(struct.pack('<I', byte_rate))
        sample_file.write(struct.pack('<H', num_channels * bits_per_sample // 8))
        sample_file.write(struct.pack('<H', bits_per_sample))
        sample_file.write(b'data')
        sample_file.write(struct.pack('<I', data_size))
        sample_file.write(b'\x00' * data_size)
        sample_file.close()
        
        # Upload
        with open(sample_file.name, 'rb') as f:
            response = client.post('/upload_wav', 
                                   data={'file': (f, 'workflow_test.wav')},
                                   content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify file was listed
        response = client.get('/uploads')
        assert response.status_code == 200
        listed = response.get_json()
        assert len(listed['uploads']) >= 1
        
        # Delete the file
        filename = data['filename']
        response = client.delete(f'/uploads/delete/{filename}')
        assert response.status_code == 200
        
        os.unlink(sample_file.name)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
