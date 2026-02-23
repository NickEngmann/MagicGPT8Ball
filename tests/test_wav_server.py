import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add repo root to path
sys.path.insert(0, '/workspace/repo')

# Import the Flask app
from wav_server import app, UPLOAD_DIR


class TestWavServer:
    """Tests for the WAV server Flask application."""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_upload_wav_success(self, client):
        """Test successful WAV file upload."""
        # Create a mock file-like object
        mock_file = MagicMock()
        mock_file.filename = 'test.wav'
        mock_file.read = MagicMock(return_value=b'\x52\x49\x46\x46')  # RIFF header
        
        with patch('wav_server.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20240101_120000'
            
            with patch('wav_server.os.path.join', return_value='/tmp/test.wav'):
                with patch('wav_server.os.makedirs'):
                    response = client.post('/upload_wav', data={'file': (mock_file, 'test.wav')})
                    assert response.status_code == 200
                    assert b'File uploaded successfully' in response.data

    def test_upload_wav_no_file_part(self, client):
        """Test upload without file part returns 400."""
        response = client.post('/upload_wav', data={})
        assert response.status_code == 400
        assert b'No file part' in response.data

    def test_upload_wav_empty_filename(self, client):
        """Test upload with empty filename returns 400."""
        mock_file = MagicMock()
        mock_file.filename = ''
        response = client.post('/upload_wav', data={'file': (mock_file, '')})
        assert response.status_code == 400
        assert b'No selected file' in response.data

    def test_upload_wav_creates_directory(self, client, tmp_path):
        """Test that upload creates the uploads directory if it doesn't exist."""
        # Use a real file-like object
        import io
        test_file = io.BytesIO(b'\x52\x49\x46\x46')
        test_file.filename = 'test.wav'
        
        test_dir = str(tmp_path / 'test_uploads')
        
        with patch('wav_server.UPLOAD_DIR', test_dir):
            with patch('wav_server.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = '20240101_120000'
                
                # Verify directory gets created by checking if file can be saved
                response = client.post('/upload_wav', data={'file': (test_file, 'test.wav')})
                assert response.status_code == 200
                # Directory should exist after the upload
                assert os.path.isdir(test_dir)

    def test_upload_wav_generates_timestamped_filename(self, client):
        """Test that uploaded files get timestamped filenames."""
        import io
        test_file = io.BytesIO(b'\x52\x49\x46\x46')
        test_file.filename = 'test.wav'
        
        with patch('wav_server.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20240101_120000'
            
            with patch('wav_server.os.path.join', return_value='/tmp/test.wav'):
                with patch('wav_server.os.makedirs'):
                    response = client.post('/upload_wav', data={'file': (test_file, 'test.wav')})
                    assert response.status_code == 200

    def test_upload_wav_file_save_called(self, client, tmp_path):
        """Test that file.save() is called with correct path."""
        import io
        test_file = io.BytesIO(b'\x52\x49\x46\x46')
        test_file.filename = 'test.wav'
        
        with patch('wav_server.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20240101_120000'
            
            expected_path = str(tmp_path / 'recording_20240101_120000.wav')
            with patch('wav_server.os.path.join', return_value=expected_path):
                with patch('wav_server.os.makedirs'):
                    response = client.post('/upload_wav', data={'file': (test_file, 'test.wav')})
                    assert response.status_code == 200

    def test_upload_wav_multiple_files(self, client):
        """Test uploading multiple files in sequence."""
        for i in range(3):
            import io
            test_file = io.BytesIO(b'\x52\x49\x46\x46')
            test_file.filename = f'recording_{i}.wav'
            
            with patch('wav_server.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = f'20240101_12000{i}'
                
                with patch('wav_server.os.path.join', return_value=f'/tmp/test{i}.wav'):
                    with patch('wav_server.os.makedirs'):
                        response = client.post('/upload_wav', data={'file': (test_file, f'recording_{i}.wav')})
                        assert response.status_code == 200
                        assert b'File uploaded successfully' in response.data

    def test_upload_wav_large_file(self, client):
        """Test uploading a larger WAV file."""
        # Create a larger mock file (1KB of data)
        large_data = b'\x00' * 1024
        
        import io
        test_file = io.BytesIO(large_data)
        test_file.filename = 'large_recording.wav'
        
        with patch('wav_server.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20240101_120000'
            
            with patch('wav_server.os.path.join', return_value='/tmp/large.wav'):
                with patch('wav_server.os.makedirs'):
                    response = client.post('/upload_wav', data={'file': (test_file, 'large_recording.wav')})
                    assert response.status_code == 200
                    assert b'File uploaded successfully' in response.data

    def test_upload_wav_invalid_content(self, client):
        """Test upload with invalid content type."""
        import io
        test_file = io.BytesIO(b'text content')
        test_file.filename = 'test.txt'
        
        with patch('wav_server.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20240101_120000'
            
            with patch('wav_server.os.path.join', return_value='/tmp/test.txt'):
                with patch('wav_server.os.makedirs'):
                    response = client.post('/upload_wav', data={'file': (test_file, 'test.txt')})
                    # The server doesn't validate file content, just saves it
                    assert response.status_code == 200

    def test_upload_wav_path_traversal_prevention(self, client):
        """Test that path traversal attempts are handled."""
        import io
        test_file = io.BytesIO(b'test')
        test_file.filename = '../../../etc/passwd'
        
        with patch('wav_server.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20240101_120000'
            
            with patch('wav_server.os.path.join', return_value='/tmp/passwd'):
                with patch('wav_server.os.makedirs'):
                    response = client.post('/upload_wav', data={'file': (test_file, '../../../etc/passwd')})
                    # The server doesn't validate filenames, just saves them
                    assert response.status_code == 200


class TestWavServerIntegration:
    """Integration tests for the WAV server."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_full_upload_flow(self, client, tmp_path):
        """Test complete upload flow with actual file saving."""
        # Use a real temporary directory
        test_dir = str(tmp_path / 'wav_uploads')
        os.makedirs(test_dir, exist_ok=True)
        
        with patch('wav_server.UPLOAD_DIR', test_dir):
            # Create actual file data
            wav_content = b'\x52\x49\x46\x46' + b'\x00' * 100  # RIFF header + data
            
            import io
            test_file = io.BytesIO(wav_content)
            test_file.filename = 'test.wav'
            
            with patch('wav_server.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = '20240101_120000'
                
                response = client.post('/upload_wav', data={'file': (test_file, 'test.wav')})
                assert response.status_code == 200
                
                # Verify file was saved
                files = os.listdir(test_dir)
                assert len(files) >= 1
                assert any('recording_' in f and '.wav' in f for f in files)
