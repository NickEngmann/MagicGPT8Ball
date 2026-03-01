from flask import Flask, request
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = 'wav_uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if file is present in request
    if 'file' not in request.files:
        return 'No file part in request', 400
    
    file = request.files['file']
    
    # Check if file is selected
    if file.filename == '':
        return 'No file selected', 400
    
    # Check if file extension is allowed
    if not allowed_file(file.filename):
        return 'File type not allowed. Allowed types: wav, mp3, ogg', 400
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Add timestamp to filename to prevent overwrites
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{filename}"
    
    # Save the file
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)
    print(f"Saved file: {filepath}")
    
    return 'File uploaded successfully', 200

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'upload_dir': UPLOAD_DIR}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
