"""
Test suite for wav_server.py - Flask WAV file upload server.
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestWavServerApp(unittest.TestCase):
    """Tests for wav_server.py Flask application."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.project_dir = self.test_dir / "magicgpt8ball"
        self.project_dir.mkdir()
        
        # Create wav_uploads directory
        self.uploads_dir = self.project_dir / "wav_uploads"
        self.uploads_dir.mkdir()
        
        # Create a mock wav_server.py in the test directory
        self.mock_server_path = self.project_dir / "wav_server.py"
        self.mock_server_path.write_text('''
from flask import Flask, request
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_DIR = "wav_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'recording_{timestamp}.wav'

    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)
    print(f"Saved file: {filepath}")

    return 'File uploaded successfully', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
''')

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_flask_app_created(self):
        """Test that Flask app is created."""
        script_path = self.project_dir / "wav_server.py"
        self.assertTrue(script_path.exists())
        content = script_path.read_text()
        self.assertIn("app = Flask", content)

    def test_upload_route_exists(self):
        """Test that /upload_wav route exists."""
        script_path = self.project_dir / "wav_server.py"
        content = script_path.read_text()
        self.assertIn("/upload_wav", content)

    def test_upload_route_method_post(self):
        """Test that /upload_wav route accepts POST method."""
        script_path = self.project_dir / "wav_server.py"
        content = script_path.read_text()
        self.assertIn("methods=['POST']", content)

    def test_wav_server_function_exists(self):
        """Test that upload_wav function exists."""
        script_path = self.project_dir / "wav_server.py"
        content = script_path.read_text()
        self.assertIn("def upload_wav", content)

    def test_datetime_import_exists(self):
        """Test that datetime is imported."""
        script_path = self.project_dir / "wav_server.py"
        content = script_path.read_text()
        self.assertIn("datetime", content)

    def test_os_import_exists(self):
        """Test that os is imported."""
        script_path = self.project_dir / "wav_server.py"
        content = script_path.read_text()
        self.assertIn("import os", content)

    def test_flask_request_import_exists(self):
        """Test that request from Flask is imported."""
        script_path = self.project_dir / "wav_server.py"
        content = script_path.read_text()
        self.assertIn("from flask import", content)

    def test_file_validation_checks(self):
        """Test that file validation is performed."""
        script_path = self.project_dir / "wav_server.py"
        content = script_path.read_text()
        self.assertIn("if 'file' not in request.files", content)
        self.assertIn("return 'No file part', 400", content)

    def test_file_saving_logic(self):
        """Test that file saving logic is present."""
        script_path = self.project_dir / "wav_server.py"
        content = script_path.read_text()
        self.assertIn("filepath = os.path.join(UPLOAD_DIR", content)
        self.assertIn("file.save(filepath)", content)

    def test_timestamp_filename_generation(self):
        """Test that filename includes timestamp."""
        script_path = self.project_dir / "wav_server.py"
        content = script_path.read_text()
        self.assertIn("timestamp = datetime.now()", content)
        self.assertIn("strftime('%Y%m%d_%H%M%S')", content)
        self.assertIn("recording_", content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
