from flask import Flask, request, jsonify
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = 'wav_uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed extensions
ALLOWED_EXTENSIONS = {'wav'}

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    # Check if file part exists
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check if file has allowed extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Only .wav files are accepted'}), 400
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Create filename with timestamp if original filename is empty after securing
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'recording_{timestamp}.wav'
    else:
        # Remove timestamp from original filename if present and add our own
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(filename)[0]
        filename = f'{base_name}_{timestamp}.wav'
    
    # Save the file
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)
    print(f"Saved file: {filepath}")
    
    return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/uploads', methods=['GET'])
def list_uploads():
    """List all uploaded files"""
    try:
        files = os.listdir(UPLOAD_DIR)
        return jsonify({'files': files, 'count': len(files)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)