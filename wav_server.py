from flask import Flask, request, jsonify
import os
from datetime import datetime
import wave
import struct

app = Flask(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = 'wav_uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Track uploaded files for listing
uploaded_files = []

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'upload_dir': UPLOAD_DIR,
        'files_count': len(uploaded_files)
    }), 200

@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    """Handle WAV file upload from the Magic 8 Ball device"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Validate WAV file format
    if not file.filename.lower().endswith('.wav'):
        return jsonify({'error': 'File must be a WAV file'}), 400
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'recording_{timestamp}.wav'
    
    # Save the file
    filepath = os.path.join(UPLOAD_DIR, filename)
    try:
        file.save(filepath)
        
        # Validate it's a proper WAV file
        if not is_valid_wav(filepath):
            os.remove(filepath)
            return jsonify({'error': 'Invalid WAV file format'}), 400
        
        # Get file info
        file_info = get_wav_info(filepath)
        
        # Track the uploaded file
        uploaded_files.append({
            'filename': filename,
            'filepath': filepath,
            'timestamp': timestamp,
            'size_bytes': file_info['size'],
            'duration_seconds': file_info['duration']
        })
        
        print(f"Saved file: {filepath} - {file_info['duration']}s, {file_info['size']} bytes")
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'duration_seconds': file_info['duration'],
            'size_bytes': file_info['size']
        }), 200
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/list_files', methods=['GET'])
def list_files():
    """List all uploaded WAV files"""
    return jsonify({
        'files': uploaded_files,
        'total_count': len(uploaded_files)
    }), 200

@app.route('/files', methods=['GET'])
def list_files_endpoint():
    """Alias for /list_files"""
    return list_files()

@app.route('/upload_wav', methods=['GET'])
def list_wav_files():
    """List uploaded WAV files when accessing /upload_wav via GET"""
    return list_files()

def is_valid_wav(filepath):
    """Validate that a file is a proper WAV format"""
    try:
        with wave.open(filepath, 'rb') as wav_file:
            # Check it's a valid WAV file
            if wav_file.getnchannels() < 1:
                return False
            if wav_file.getsampwidth() not in [1, 2, 3, 4]:
                return False
            return True
    except Exception:
        return False

def get_wav_info(filepath):
    """Get information about a WAV file"""
    with wave.open(filepath, 'rb') as wav_file:
        n_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        
        # Calculate duration
        duration = n_frames / float(frame_rate) if frame_rate > 0 else 0
        
        # Calculate size in bytes
        size = n_frames * n_channels * sample_width
        
        return {
            'channels': n_channels,
            'sample_width': sample_width,
            'sample_rate': frame_rate,
            'duration': duration,
            'size': size
        }

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get upload statistics"""
    total_size = sum(f['size_bytes'] for f in uploaded_files)
    total_duration = sum(f['duration_seconds'] for f in uploaded_files)
    
    return jsonify({
        'total_files': len(uploaded_files),
        'total_size_bytes': total_size,
        'total_duration_seconds': total_duration,
        'average_duration': total_duration / len(uploaded_files) if uploaded_files else 0,
        'upload_dir': UPLOAD_DIR
    }), 200

if __name__ == '__main__':
    print("WAV Server starting...")
    print(f"Upload directory: {UPLOAD_DIR}")
    print("Endpoints:")
    print("  GET  /health          - Health check")
    print("  GET  /list_files      - List all uploaded files")
    print("  GET  /files           - Alias for /list_files")
    print("  GET  /stats           - Upload statistics")
    print("  POST /upload_wav      - Upload a WAV file")
    print("  GET  /upload_wav      - List files (same as /list_files)")
    app.run(host='0.0.0.0', port=5000, debug=True)
