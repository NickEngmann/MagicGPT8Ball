from flask import Flask, request, jsonify
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_DIR = 'wav_uploads'
ALLOWED_EXTENSIONS = {'wav'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    # Check if file part exists
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Check if file was selected
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Validate filename and extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only .wav files allowed'}), 400
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Create timestamped filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    unique_filename = f'{name}_{timestamp}{ext}'
    
    # Save the file
    filepath = os.path.join(UPLOAD_DIR, unique_filename)
    try:
        file.save(filepath)
        print(f"Saved file: {filepath}")
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': unique_filename,
            'filepath': filepath
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'upload_dir': UPLOAD_DIR}), 200

@app.route('/uploads', methods=['GET'])
def list_uploads():
    """List all uploaded files."""
    try:
        files = os.listdir(UPLOAD_DIR)
        return jsonify({'files': files, 'count': len(files)}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to list uploads: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
