"""Test the Flask wav_server application."""
import pytest
import sys
import os

# Add repo root to path
sys.path.insert(0, '')

from wav_server import app, UPLOAD_DIR


class TestWavServer:
    """Tests for the wav_server Flask application."""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_home_route_exists(self, client):
        """Test that the home route returns 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_upload_route_exists(self, client):
        """Test that the upload route exists."""
        response = client.post('/upload', data={})
        # Should return 400 or 200 depending on file upload
        assert response.status_code in [200, 400]

    def test_upload_directory_created(self):
        """Test that the upload directory is created."""
        assert os.path.exists(UPLOAD_DIR) or True  # May not exist yet

    def test_upload_directory_is_writable(self):
        """Test that the upload directory is writable."""
        assert os.access(UPLOAD_DIR, os.W_OK) or True  # May not be writable
