from flask import Flask, request
import os
from datetime import datetime

app = Flask(__name__)

# Configure uploads directory
app.config['UPLOAD_DIR'] = os.environ.get('WAV_UPLOAD_DIR', 'wav_uploads')
os.makedirs(app.config['UPLOAD_DIR'], exist_ok=True)

# Export for testing access
UPLOAD_DIR = app.config['UPLOAD_DIR']


@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    """Handle WAV file uploads"""
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'recording_{timestamp}.wav'

    # Save the file
    filepath = os.path.join(app.config['UPLOAD_DIR'], filename)
    file.save(filepath)
    print(f"Saved file: {filepath}")

    return 'File uploaded successfully', 200


def get_upload_dir():
    """Get the current upload directory path"""
    return app.config['UPLOAD_DIR']


def set_upload_dir(path):
    """Set the upload directory path (useful for testing)"""
    app.config['UPLOAD_DIR'] = path
    os.makedirs(path, exist_ok=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)