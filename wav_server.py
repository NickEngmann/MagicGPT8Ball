from flask import Flask, request, jsonify
import os
import wave
import contextlib
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
UPLOAD_DIR = 'wav_uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)


def is_valid_wav_file(filepath):
    """Validate that the file is a proper WAV file."""
    try:
        with contextlib.closing(wave.open(filepath, 'r')) as f:
            # Check basic WAV properties
            channels = f.getnchannels()
            sampwidth = f.getsampwidth()
            framerate = f.getframerate()
            comptype = f.getcomptype()
            
            # Validate WAV properties
            if channels not in [1, 2]:
                return False
            if sampwidth not in [1, 2, 4]:
                return False
            if framerate < 8000 or framerate > 48000:
                return False
            if comptype != 'NONE':
                return False
            return True
    except Exception as e:
        logger.warning(f"Invalid WAV file: {e}")
        return False


@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    """Upload a WAV file to the server."""
    # Check if file is present in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    
    file = request.files['file']
    
    # Check if file was selected
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Validate file extension
    if not file.filename.lower().endswith('.wav'):
        return jsonify({'error': 'Invalid file type. Only .wav files are allowed'}), 400
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'recording_{timestamp}.wav'
    
    # Save the file to a temporary location first for validation
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    try:
        file.save(filepath)
        logger.info(f"Saved file: {filepath}")
        
        # Validate the saved file is a proper WAV
        if not is_valid_wav_file(filepath):
            os.remove(filepath)
            return jsonify({'error': 'Invalid WAV file format'}), 400
        
        logger.info(f"Valid WAV file saved: {filepath}")
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'size': os.path.getsize(filepath)
        }), 200
        
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        # Clean up if file was partially saved
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': 'Failed to save file'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'upload_dir': UPLOAD_DIR,
        'max_file_size_mb': MAX_FILE_SIZE // (1024 * 1024)
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with basic information."""
    return jsonify({
        'service': 'MagicGPT8Ball WAV Server',
        'version': '1.1.0',
        'endpoints': [
            {'path': '/upload_wav', 'method': 'POST', 'description': 'Upload a WAV file'},
            {'path': '/health', 'method': 'GET', 'description': 'Health check'}
        ]
    }), 200


if __name__ == '__main__':
    logger.info("Starting MagicGPT8Ball WAV Server...")
    app.run(host='0.0.0.0', port=5000, debug=False)
