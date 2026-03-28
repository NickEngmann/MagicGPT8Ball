from flask import Flask, request, jsonify
import os
from datetime import datetime
import hashlib
import json
from pathlib import Path

app = Flask(__name__)

# Configuration
UPLOAD_DIR = 'wav_uploads'
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {'.wav'}
RECORDINGS_INDEX_FILE = 'wav_uploads/recordings_index.json'

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_file_size_mb(file):
    """Get file size in megabytes."""
    file.seek(0, 2)  # Seek to end
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)  # Reset to beginning
    return size_mb

def validate_wav_file(file):
    """Validate that the uploaded file is a proper WAV file."""
    # Check file signature (RIFF header)
    file.seek(0)
    header = file.read(12)
    
    # WAV files should start with 'RIFF'
    if not header.startswith(b'RIFF'):
        return False, "Invalid file: Not a WAV file (missing RIFF header)"
    
    # Check for 'WAVE' format
    if not header[8:12] == b'WAVE':
        return False, "Invalid file: Not a WAV file (missing WAVE format)"
    
    return True, "Valid WAV file"

def load_recordings_index():
    """Load the recordings index from JSON file."""
    if os.path.exists(RECORDINGS_INDEX_FILE):
        try:
            with open(RECORDINGS_INDEX_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"recordings": []}
    return {"recordings": []}

def save_recordings_index(index_data):
    """Save the recordings index to JSON file."""
    try:
        with open(RECORDINGS_INDEX_FILE, 'w') as f:
            json.dump(index_data, f, indent=2)
    except IOError as e:
        print(f"Error saving index: {e}")

def generate_unique_filename(original_filename):
    """Generate a unique filename based on timestamp and hash."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Add randomness to prevent collisions if multiple uploads in same second
    timestamp += f'_{datetime.now().microsecond:06d}'
    
    # Sanitize original filename
    name, ext = os.path.splitext(original_filename)
    safe_name = ''.join(c if c.isalnum() or c in ' _-' else '_' for c in name)
    
    filename = f'{safe_name}_{timestamp}{ext.lower() if ext else ".wav"}'
    return filename

@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    """Upload a WAV file with validation and metadata tracking."""
    # Check if file part exists
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({'success': False, 'error': f'Invalid file type: {ext}. Only WAV files allowed'}), 400
    
    # Check file size
    try:
        size_mb = get_file_size_mb(file)
        if size_mb > MAX_FILE_SIZE_MB:
            return jsonify({
                'success': False,
                'error': f'File too large: {size_mb:.2f}MB. Maximum allowed is {MAX_FILE_SIZE_MB}MB'
            }), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error checking file size: {str(e)}'}), 400
    
    # Validate WAV file format
    is_valid, message = validate_wav_file(file)
    if not is_valid:
        return jsonify({'success': False, 'error': message}), 400
    
    # Generate unique filename
    filename = generate_unique_filename(file.filename)
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Save the file
    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to save file: {str(e)}'}), 500
    
    # Calculate file hash for integrity
    file.seek(0)
    file_hash = hashlib.sha256(file.read()).hexdigest()
    
    # Update recordings index
    index = load_recordings_index()
    recording_info = {
        'filename': filename,
        'filepath': filepath,
        'original_filename': file.filename,
        'size_bytes': os.path.getsize(filepath),
        'size_mb': round(size_mb, 2),
        'uploaded_at': datetime.now().isoformat(),
        'hash': file_hash
    }
    index['recordings'].insert(0, recording_info)  # Add to beginning (most recent first)
    save_recordings_index(index)
    
    # Log the upload
    print(f"Saved file: {filepath}")
    print(f"File: {filename}, Size: {size_mb:.2f}MB, Hash: {file_hash[:16]}...")
    
    return jsonify({
        'success': True,
        'message': 'File uploaded successfully',
        'filename': filename,
        'size_mb': round(size_mb, 2),
        'hash': file_hash
    }), 201

@app.route('/recordings', methods=['GET'])
def list_recordings():
    """List all uploaded recordings."""
    index = load_recordings_index()
    recordings = index.get('recordings', [])
    
    # Format for API response
    formatted_recordings = []
    for r in recordings:
        formatted_recordings.append({
            'filename': r['filename'],
            'original_filename': r['original_filename'],
            'size_mb': r['size_mb'],
            'uploaded_at': r['uploaded_at'],
            'filepath': r['filepath'],
            'hash': r['hash']
        })
    
    return jsonify({
        'success': True,
        'count': len(formatted_recordings),
        'recordings': formatted_recordings
    }), 200

@app.route('/recordings/<filename>', methods=['GET'])
def get_recording(filename):
    """Get information about a specific recording."""
    index = load_recordings_index()
    recordings = index.get('recordings', [])
    
    for r in recordings:
        if r['filename'] == filename or r['filepath'] == filename:
            return jsonify({
                'success': True,
                'recording': {
                    'filename': r['filename'],
                    'original_filename': r['original_filename'],
                    'size_mb': r['size_mb'],
                    'uploaded_at': r['uploaded_at'],
                    'filepath': r['filepath'],
                    'hash': r['hash']
                }
            }), 200
    
    return jsonify({'success': False, 'error': 'Recording not found'}), 404

@app.route('/recordings/<filename>', methods=['DELETE'])
def delete_recording(filename):
    """Delete a recording by filename."""
    index = load_recordings_index()
    recordings = index.get('recordings', [])
    
    for i, r in enumerate(recordings):
        if r['filename'] == filename or r['filepath'] == filename:
            try:
                filepath = r['filepath']
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"Deleted file: {filepath}")
                
                # Remove from index
                recordings.pop(i)
                index['recordings'] = recordings
                save_recordings_index(index)
                
                return jsonify({
                    'success': True,
                    'message': f'Recording "{filename}" deleted successfully'
                }), 200
            except Exception as e:
                return jsonify({'success': False, 'error': f'Failed to delete file: {str(e)}'}), 500
    
    return jsonify({'success': False, 'error': 'Recording not found'}), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'upload_dir': UPLOAD_DIR,
        'max_file_size_mb': MAX_FILE_SIZE_MB
    }), 200

@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint."""
    return jsonify({
        'service': 'WAV Server API',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'API documentation',
            'GET /health': 'Health check',
            'GET /recordings': 'List all recordings',
            'GET /recordings/<filename>': 'Get recording information',
            'DELETE /recordings/<filename>': 'Delete a recording',
            'POST /upload_wav': 'Upload a WAV file'
        },
        'configuration': {
            'upload_dir': UPLOAD_DIR,
            'max_file_size_mb': MAX_FILE_SIZE_MB,
            'allowed_extensions': list(ALLOWED_EXTENSIONS)
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)