from flask import Flask, request, jsonify
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)

# Configuration
UPLOAD_DIR = os.environ.get('UPLOAD_DIR', 'wav_uploads')
MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB default
ALLOWED_EXTENSIONS = {'wav'}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def file_size_limit(max_size):
    """Decorator to limit file upload size."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Check Content-Length header
            content_length = request.content_length
            if content_length and content_length > max_size:
                return jsonify({'error': 'File too large'}), 413
            return f(*args, **kwargs)
        return wrapped
    return decorator


@app.route('/upload_wav', methods=['POST'])
@file_size_limit(MAX_FILE_SIZE)
def upload_wav():
    """Handle WAV file uploads."""
    # Check if file is present in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check if file has allowed extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only .wav files allowed'}), 400
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = os.path.splitext(filename)[0]
    filename = f'{base_name}_{timestamp}.wav'
    
    # Save the file
    filepath = os.path.join(UPLOAD_DIR, filename)
    try:
        file.save(filepath)
        print(f"Saved file: {filepath}")
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'filepath': filepath
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'upload_dir': UPLOAD_DIR,
        'max_file_size': MAX_FILE_SIZE
    }), 200


@app.route('/clear_uploads', methods=['POST'])
def clear_uploads():
    """Clear all uploaded files (for testing/admin)."""
    try:
        for filename in os.listdir(UPLOAD_DIR):
            filepath = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        return jsonify({'message': 'Uploads cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to clear uploads: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
