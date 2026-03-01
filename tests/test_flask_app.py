import pytest
import sys
import os

# Add the repo root to the path to find the app
sys.path.insert(0, '')

from flask import Flask


class TestFlaskApp:
    """Tests for the Flask WAV upload server"""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app"""
        # Import the app - adjust import based on actual app structure
        try:
            from app import app
        except ImportError:
            # Try alternative import paths
            try:
                import main
                app = main.app
            except ImportError:
                # Create a simple test app if main app can't be imported
                app = Flask(__name__)
        
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.test_client() as client:
            yield client
    
    def test_home_page(self, client):
        """Test that the home page loads"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_upload_page(self, client):
        """Test that the upload page loads"""
        response = client.get('/upload')
        assert response.status_code == 200
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        assert b'healthy' in response.data.lower() or b'ok' in response.data.lower()

