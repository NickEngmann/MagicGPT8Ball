from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Default upload directory
DEFAULT_UPLOAD_DIR = 'wav_uploads'
app.config['UPLOAD_FOLDER'] = DEFAULT_UPLOAD_DIR

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Track uploaded files for status endpoint
uploaded_files = []

# Helper function to get upload folder
get_upload_folder = lambda: app.config.get('UPLOAD_FOLDER', DEFAULT_UPLOAD_DIR)

@app.route('/upload', methods=['POST'])
def upload_wav():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'recording_{timestamp}.wav'
    
    # Save the file
    filepath = os.path.join(get_upload_folder(), filename)
    file.save(filepath)
    print(f"Saved file: {filepath}")
    
    # Track the file
    uploaded_files.append({
        'filename': filename,
        'filepath': filepath,
        'size': os.path.getsize(filepath)
    })
    
    return 'File uploaded successfully', 200

@app.route('/status', methods=['GET'])
def status():
    """Return status of the wav server."""
    return jsonify({
        'status': 'running',
        'upload_dir': get_upload_folder(),
        'files_uploaded': len(uploaded_files)
    }), 200

@app.route('/files', methods=['GET'])
def list_files():
    """Return list of uploaded files."""
    return jsonify({
        'files': uploaded_files,
        'count': len(uploaded_files)
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
