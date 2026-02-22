import os
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
UPLOAD_DIR = 'wav_uploads'

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.wav'):
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'recording_{timestamp}.wav'
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # Ensure directory exists (in case of race conditions or direct calls)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully'}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400


if __name__ == '__main__':
    app.run(debug=True)