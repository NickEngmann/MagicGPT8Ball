from flask import Flask, request, jsonify
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import magic

app = Flask(__name__)

# Configuration
UPLOAD_DIR = 'wav_uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB max file size
ALLOWED_EXTENSIONS = {'wav'}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize file type checker
file_magic = magic.Magic(mime=True)


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_valid_wav(filepath):
    """Check if the file is actually a WAV file by examining its header."""
    try:
        with open(filepath, 'rb') as f:
            # WAV files start with 'RIFF' header
            header = f.read(12)
            if len(header) < 12:
                return False
            # Check for RIFF and WAVE signatures
            if header[:4] != b'RIFF' or header[8:12] != b'WAVE':
                return False
            return True
    except Exception:
        return False


@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    # Check if file is present in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    
    file = request.files['file']
    
    # Check if a file was selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Check if file has allowed extension
    if not allowed_file(filename):
        return jsonify({'error': 'Invalid file type. Only .wav files are allowed'}), 400
    
    # Check file size
    file.seek(0, 2)  # Move to end of file
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': f'File size exceeds {MAX_FILE_SIZE // (1024*1024)} MB limit'}), 413
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = filename.rsplit('.', 1)[0]  # Remove extension
    safe_name = safe_name.replace(' ', '_')  # Replace spaces with underscores
    filename = f'{safe_name}_{timestamp}.wav'
    
    # Save the file
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)
    
    # Validate that it's actually a WAV file
    if not is_valid_wav(filepath):
        os.remove(filepath)
        return jsonify({'error': 'Invalid WAV file format'}), 400
    
    file_size_kb = os.path.getsize(filepath) / 1024
    
    return jsonify({
        'message': 'File uploaded successfully',
        'filename': filename,
        'filepath': filepath,
        'size_kb': round(file_size_kb, 2),
        'timestamp': timestamp
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'upload_dir': UPLOAD_DIR,
        'max_file_size_mb': MAX_FILE_SIZE // (1024*1024)
    }), 200


@app.route('/list_files', methods=['GET'])
def list_files():
    """List all uploaded WAV files."""
    try:
        files = []
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith('.wav'):
                filepath = os.path.join(UPLOAD_DIR, filename)
                files.append({
                    'filename': filename,
                    'size_kb': round(os.path.getsize(filepath) / 1024, 2),
                    'created': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                })
        return jsonify({'files': files, 'total': len(files)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete_file/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a specific uploaded file."""
    try:
        filename = secure_filename(filename)
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'message': f'File {filename} deleted successfully'}), 200
        else:
            return jsonify({'error': f'File {filename} not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
