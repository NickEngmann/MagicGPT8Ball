from flask import Flask, request, jsonify
import os
from datetime import datetime
import struct
import hashlib
import re


app = Flask(__name__)

# Configuration
UPLOAD_DIR = os.path.join(os.getcwd(), 'wav_uploads')
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes
os.makedirs(UPLOAD_DIR, exist_ok=True)


def sanitize_filename(filename):
    """Sanitize filename to prevent directory traversal attacks."""
    # Get basename to remove any path components
    safe_name = os.path.basename(filename)
    # Remove any non-alphanumeric characters except dots, underscores, hyphens
    safe_name = re.sub(r'[^\w\-\.]', '_', safe_name)
    return safe_name


def validate_wav_header(filepath):
    """
    Validate a WAV file header.
    
    Returns a dict with validation results including:
    - valid: bool
    - sample_rate: int (if valid)
    - num_channels: int (if valid)
    - bits_per_sample: int (if valid)
    - duration_seconds: float (if valid)
    - error: str (if invalid)
    """
    result = {
        'valid': False,
        'sample_rate': None,
        'num_channels': None,
        'bits_per_sample': None,
        'duration_seconds': None,
        'error': None
    }
    
    # Check if file exists
    if not os.path.exists(filepath):
        result['error'] = 'File not found'
        return result
    
    try:
        file_size = os.path.getsize(filepath)
        
        # File must be at least 44 bytes for a minimal WAV header
        if file_size < 44:
            result['error'] = 'File too small to be a valid WAV file'
            return result
        
        with open(filepath, 'rb') as f:
            # Read RIFF header
            riff_header = f.read(4)
            if riff_header != b'RIFF':
                result['error'] = 'Invalid RIFF header'
                return result
            
            # Read file size (skip)
            file_size_bytes = f.read(4)
            file_size = struct.unpack('<I', file_size_bytes)[0]
            
            # Read WAVE signature
            wave_sig = f.read(4)
            if wave_sig != b'WAVE':
                result['error'] = 'Invalid WAV signature'
                return result
            
            # Find fmt chunk
            fmt_chunk_found = False
            data_chunk_found = False
            sample_rate = 0
            num_channels = 0
            bits_per_sample = 0
            byte_rate = 0
            data_size = 0
            
            while True:
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    break
                
                chunk_id = chunk_header[:4]
                chunk_size = struct.unpack('<I', chunk_header[4:8])[0]
                
                if chunk_id == b'fmt ':
                    fmt_chunk_found = True
                    # Read fmt chunk data
                    fmt_data = f.read(chunk_size)
                    
                    if len(fmt_data) >= 16:
                        audio_format = struct.unpack('<H', fmt_data[0:2])[0]
                        num_channels = struct.unpack('<H', fmt_data[2:4])[0]
                        sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
                        byte_rate = struct.unpack('<I', fmt_data[8:12])[0]
                        bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
                        
                        # Only support PCM (audio_format == 1)
                        if audio_format != 1:
                            result['error'] = f'Unsupported audio format: {audio_format}'
                            return result
                elif chunk_id == b'data':
                    data_chunk_found = True
                    data_size = chunk_size
                    break
                else:
                    # Skip unknown chunks
                    f.seek(chunk_size, 1)
            
            if not fmt_chunk_found:
                result['error'] = 'Missing fmt chunk'
                return result
            
            if not data_chunk_found:
                result['error'] = 'Missing data chunk'
                return result
            
            # Validate we have enough data
            if data_size == 0:
                result['error'] = 'Data chunk has zero size'
                return result
            
            # Calculate duration
            duration = data_size / byte_rate if byte_rate > 0 else 0
            
            result['valid'] = True
            result['sample_rate'] = sample_rate
            result['num_channels'] = num_channels
            result['bits_per_sample'] = bits_per_sample
            result['duration_seconds'] = round(duration, 3)
            return result
            
    except IOError as e:
        result['error'] = f'IO error reading file: {str(e)}'
        return result
    except struct.error as e:
        result['error'] = f'Malformed WAV header: {str(e)}'
        return result
    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)}'
        return result


def generate_checksum(filepath):
    """
    Generate MD5 checksum for a file.
    
    Returns the hex digest of the MD5 hash, or an error message if the file
    cannot be read.
    """
    if not os.path.exists(filepath):
        return f"Error: File not found: {filepath}"
    
    try:
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            # Read file in chunks for memory efficiency
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except IOError as e:
        return f"Error: Could not read file: {str(e)}"


def cleanup_old_uploads(max_age_hours=24):
    """
    Delete uploaded WAV files older than the specified age.
    
    Args:
        max_age_hours: Maximum age of files to keep in hours.
        
    Returns:
        dict with cleanup results including deleted count and files.
    """
    result = {
        'success': True,
        'deleted_count': 0,
        'deleted_files': [],
        'error': None
    }
    
    if not os.path.exists(UPLOAD_DIR):
        result['error'] = 'Upload directory does not exist'
        return result
    
    current_time = datetime.now().timestamp()
    max_age_seconds = max_age_hours * 3600
    
    try:
        for filename in os.listdir(UPLOAD_DIR):
            filepath = os.path.join(UPLOAD_DIR, filename)
            
            # Skip directories
            if os.path.isdir(filepath):
                continue
            
            # Check file age
            file_mtime = os.path.getmtime(filepath)
            age_seconds = current_time - file_mtime
            
            if age_seconds > max_age_seconds:
                try:
                    os.remove(filepath)
                    result['deleted_count'] += 1
                    result['deleted_files'].append(filename)
                except OSError as e:
                    result['error'] = f"Could not delete {filename}: {str(e)}"
                    result['success'] = False
    
    except OSError as e:
        result['success'] = False
        result['error'] = f"Error listing upload directory: {str(e)}"
    
    return result


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'upload_directory': UPLOAD_DIR,
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024)
    }), 200


@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    """Upload a single WAV file with validation."""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file part'
        }), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No selected file'
        }), 400
    
    # Sanitize filename
    original_filename = sanitize_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'recording_{timestamp}_{original_filename}'
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Check file size before saving
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Seek back to start
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({
            'success': False,
            'error': f'File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)} MB'
        }), 400
    
    # Save the file
    try:
        file.save(filepath)
    except IOError as e:
        return jsonify({
            'success': False,
            'error': f'Could not save file: {str(e)}'
        }), 500
    
    # Validate WAV header
    validation = validate_wav_header(filepath)
    if not validation['valid']:
        # Remove invalid file
        try:
            os.remove(filepath)
        except:
            pass
        
        # Return custom error message for invalid WAV files
        error_msg = validation['error']
        if 'File too small' in error_msg or 'Invalid RIFF' in error_msg or 'Invalid WAV' in error_msg or 'Missing' in error_msg:
            error_msg = f'Invalid WAV file: {error_msg}'
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 400
    
    # Generate checksum
    checksum = generate_checksum(filepath)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'filepath': filepath,
        'file_size': file_size,
        'checksum': checksum,
        'metadata': {
            'sample_rate': validation['sample_rate'],
            'num_channels': validation['num_channels'],
            'bits_per_sample': validation['bits_per_sample'],
            'duration_seconds': validation['duration_seconds']
        }
    }), 200


@app.route('/upload_wav_batch', methods=['POST'])
def upload_wav_batch():
    """Upload multiple WAV files in a batch."""
    if 'files' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No files part'
        }), 400
    
    files = request.files.getlist('files')
    if len(files) == 0:
        return jsonify({
            'success': False,
            'error': 'No files selected'
        }), 400
    
    results = {
        'success': True,
        'uploaded_count': 0,
        'failed_count': 0,
        'files': []
    }
    
    for file in files:
        if file.filename == '':
            continue
        
        original_filename = sanitize_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'recording_{timestamp}_{original_filename}'
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        file_size = 0
        try:
            # Check file size
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                results['failed_count'] += 1
                results['files'].append({
                    'filename': filename,
                    'success': False,
                    'error': f'File too large (> {MAX_FILE_SIZE / (1024*1024)} MB)'
                })
                continue
            
            # Save file
            file.save(filepath)
            
            # Validate
            validation = validate_wav_header(filepath)
            if not validation['valid']:
                try:
                    os.remove(filepath)
                except:
                    pass
                results['failed_count'] += 1
                results['files'].append({
                    'filename': filename,
                    'success': False,
                    'error': validation['error']
                })
                continue
            
            # Generate checksum
            checksum = generate_checksum(filepath)
            
            results['uploaded_count'] += 1
            results['files'].append({
                'filename': filename,
                'filepath': filepath,
                'file_size': file_size,
                'checksum': checksum,
                'metadata': {
                    'sample_rate': validation['sample_rate'],
                    'num_channels': validation['num_channels'],
                    'bits_per_sample': validation['bits_per_sample'],
                    'duration_seconds': validation['duration_seconds']
                }
            })
            
        except IOError as e:
            results['failed_count'] += 1
            results['files'].append({
                'filename': filename,
                'success': False,
                'error': str(e)
            })
    
    return jsonify(results), 200 if results['success'] else 400


@app.route('/uploads', methods=['GET'])
def list_uploads():
    """List all uploaded WAV files with pagination."""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    if not os.path.exists(UPLOAD_DIR):
        return jsonify({
            'success': True,
            'uploads': [],
            'total': 0,
            'limit': limit,
            'offset': offset
        }), 200
    
    try:
        all_files = []
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith('.wav'):
                filepath = os.path.join(UPLOAD_DIR, filename)
                try:
                    file_size = os.path.getsize(filepath)
                    file_mtime = os.path.getmtime(filepath)
                    mtime_str = datetime.fromtimestamp(file_mtime).isoformat()
                    
                    checksum = generate_checksum(filepath)
                    
                    all_files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'file_size': file_size,
                        'created_at': mtime_str,
                        'checksum': checksum
                    })
                except OSError:
                    pass
        
        # Sort by creation time (descending)
        all_files.sort(key=lambda x: x['created_at'], reverse=True)
        
        total = len(all_files)
        
        # Apply pagination
        paginated_files = all_files[offset:offset + limit]
        
        return jsonify({
            'success': True,
            'uploads': paginated_files,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except OSError as e:
        return jsonify({
            'success': False,
            'error': f'Error listing directory: {str(e)}'
        }), 500


@app.route('/uploads/delete/<filename>', methods=['DELETE'])
def delete_upload(filename):
    """Delete a specific uploaded WAV file."""
    # Sanitize filename to prevent directory traversal
    safe_filename = sanitize_filename(filename)
    filepath = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Ensure the filepath is within UPLOAD_DIR
    if not filepath.startswith(UPLOAD_DIR):
        return jsonify({
            'success': False,
            'error': 'Invalid filename'
        }), 400
    
    if not os.path.exists(filepath):
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404
    
    try:
        os.remove(filepath)
        return jsonify({
            'success': True,
            'filename': safe_filename,
            'message': 'File deleted successfully'
        }), 200
    except OSError as e:
        return jsonify({
            'success': False,
            'error': f'Could not delete file: {str(e)}'
        }), 500


@app.route('/uploads/checksum/<filename>', methods=['GET'])
def get_checksum(filename):
    """Get the MD5 checksum of an uploaded WAV file."""
    safe_filename = sanitize_filename(filename)
    filepath = os.path.join(UPLOAD_DIR, safe_filename)
    
    if not os.path.exists(filepath):
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404
    
    checksum = generate_checksum(filepath)
    if checksum.startswith('Error:'):
        return jsonify({
            'success': False,
            'error': checksum
        }), 500
    
    return jsonify({
        'success': True,
        'filename': safe_filename,
        'checksum': checksum
    }), 200


@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up old uploaded WAV files."""
    max_age_hours = int(request.args.get('max_age_hours', 24))
    
    result = cleanup_old_uploads(max_age_hours)
    
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)