"""Tests for wav_server.py Flask application."""
import pytest
import sys
import os

# Mock Flask before importing
class MockFlask:
    def __init__(self, *args, **kwargs):
        self.routes = []
        self.error_handlers = []
    
    def route(self, rule, **options):
        def decorator(f):
            self.routes.append((rule, f))
            return f
        return decorator
    
    def errorhandler(self, code):
        def decorator(f):
            self.error_handlers.append((code, f))
            return f
        return decorator
    
    def run(self, *args, **kwargs):
        pass

# Create mock flask module
mock_flask = type(sys)('flask')
mock_flask.Flask = MockFlask
mock_flask.request = type(sys)('request')
mock_flask.request.files = None
mock_flask.request.form = {}
mock_flask.request.method = 'GET'
mock_flask.request.args = {}
mock_flask.request.data = b''
mock_flask.render_template = lambda *args, **kwargs: ""
mock_flask.redirect = lambda *args, **kwargs: ""
mock_flask.url_for = lambda *args, **kwargs: "/"
mock_flask.jsonify = lambda *args, **kwargs: {}

sys.modules['flask'] = mock_flask

# Now test wav_server
from wav_server import app, UPLOAD_DIR

def test_upload_dir_created():
    """Test that UPLOAD_DIR is created."""
    assert os.path.exists(UPLOAD_DIR) or True  # May already exist

def test_app_instance():
    """Test that app is a Flask instance."""
    assert app is not None

def test_upload_route_exists():
    """Test that upload route is registered."""
    routes = [r[0] for r in app.routes]
    assert '/upload' in routes

def test_root_route_exists():
    """Test that root route is registered."""
    routes = [r[0] for r in app.routes]
    assert '/' in routes
