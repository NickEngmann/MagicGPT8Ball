from flask import Flask, request, jsonify
import os
import re
import hashlib
import struct
from datetime import datetime, timedelta
from pathlib import PurePath

app = Flask(__name__)

# Configuration
UPLOAD_DIR = 'wav_uploads'
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)


def sanitize_filename(filename):
    """
    Sanitize a filename to prevent directory traversal attacks and remove invalid characters.
    
    Args:
        filename: Original filename to sanitize
        
    Returns:
        Sanitized filename safe for filesystem operations
    """
    # Extract just the filename to remove any path components
    path = PurePath(filename)
    safe_name = path.name
    
    # Replace spaces with underscores
    safe_name = safe_name.replace(' ', '_')
    
    # Replace special characters with underscores (keep alphanumeric, dots, underscores, hyphens)
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_name)
    
    return safe_name


def validate_wav_header(filepath):
    """
    Validate that a file is a proper WAV audio file.
    
    Args:
        filepath: Path to the WAV file
        
    Returns:
        dict: Validation result with 'valid' boolean and optional metadata/errors
    """
    result = {'valid': False}
    
    # Check if file exists
    if not os.path.exists(filepath):
        result['error'] = 'File not found'
        return result
    
    try:
        with open(filepath, 'rb') as f:
            # Read RIFF header (4 bytes)
            riff_header = f.read(4)
            if riff_header != b'RIFF':
                result['error'] = 'Invalid RIFF header'
                return result
            
            # Read file size (4 bytes)
            file_size = struct.unpack('<I', f.read(4))[0]
            
            # Read WAVE signature (4 bytes)
            wave_sig = f.read(4)
            if wave_sig != b'WAVE':
                result['error'] = 'Invalid WAV signature'
                return result
            
            # Read fmt chunk
            fmt_header = f.read(4)
            if fmt_header != b'fmt ':
                result['error'] = 'Missing fmt chunk'
                return result
            
            fmt_size = struct.unpack('<I', f.read(4))[0]
            fmt_data = f.read(fmt_size)
            
            # Parse PCM header
            if len(fmt_data) < 16:
                result['error'] = 'Invalid fmt chunk size'
                return result
            
            format_code = struct.unpack('<H', fmt_data[0:2])[0]
            num_channels = struct.unpack('<H', fmt_data[2:4])[0]
            sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
            byte_rate = struct.unpack('<I', fmt_data[8:12])[0]
            block_align = struct.unpack('<H', fmt_data[12:14])[0]
            bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
            
            if format_code != 1:
                result['error'] = 'Unsupported audio format'
                return result
            
            # Read data chunk
            data_header = f.read(4)
            if data_header != b'data':
                result['error'] = 'Missing data chunk'
                return result
            
            data_size = struct.unpack('<I', f.read(4))[0]
            
            if data_size == 0:
                result['error'] = 'Data chunk has zero size'
                return result
            
            # Validation successful
            result['valid'] = True
            result['sample_rate'] = sample_rate
            result['num_channels'] = num_channels
            result['bits_per_sample'] = bits_per_sample
            result['byte_rate'] = byte_rate
            result['duration_seconds'] = round(data_size / byte_rate, 3)
            result['file_size'] = os.path.getsize(filepath)
            
    except Exception as e:
        result['error'] = f'Validation error: {str(e)}'
    
    return result


def generate_checksum(filepath):
    """
    Generate MD5 checksum for a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        str: MD5 hex digest string or error message
    """
    if not os.path.exists(filepath):
        return 'Error: File not found'
    
    try:
        md5_hash = hashlib.md5()
        with open(filepath, 'rb') as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except Exception as e:
        return f'Error: {str(e)}'


def cleanup_old_uploads(max_age_hours=24):
    """
    Clean up WAV files older than specified hours.
    
    Args:
        max_age_hours: Maximum age of files to keep in hours
        
    Returns:
        dict: Cleanup result with statistics
    """
    result = {
        'success': True,
        'deleted_count': 0,
        'deleted_files': [],
        'preserved_count': 0,
        'error': None
    }
    
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    
    if not os.path.exists(UPLOAD_DIR):
        return result
    
    try:
        for filename in os.listdir(UPLOAD_DIR):
            if filename.lower().endswith('.wav'):
                filepath = os.path.join(UPLOAD_DIR, filename)
                
                # Get file modification time
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if mtime < cutoff_time:
                    os.remove(filepath)
                    result['deleted_count'] += 1
                    result['deleted_files'].append(filename)
                else:
                    result['preserved_count'] += 1
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
    
    return result


def health_check():
    """
    Health check endpoint handler.
    
    Returns:
        dict: Health status information
    """
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'upload_directory': UPLOAD_DIR,
        'max_file_size_mb': MAX_FILE_SIZE_MB,
        'directory_exists': os.path.exists(UPLOAD_DIR)
    }


def list_uploads(limit=50, offset=0):
    """
    List uploaded WAV files with pagination.
    
    Args:
        limit: Maximum number of files to return
        offset: Number of files to skip
        
    Returns:
        dict: List of uploaded files with metadata
    """
    if not os.path.exists(UPLOAD_DIR):
        return {'success': True, 'uploads': [], 'total': 0}
    
    try:
        all_files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith('.wav')]
        total = len(all_files)
        
        # Apply pagination
        sorted_files = sorted(all_files)
        paginated_files = sorted_files[offset:offset + limit]
        
        uploads = []
        for filename in paginated_files:
            filepath = os.path.join(UPLOAD_DIR, filename)
            file_stat = os.stat(filepath)
            uploads.append({
                'filename': filename,
                'size_bytes': file_stat.st_size,
                'created_at': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            })
        
        return {
            'success': True,
            'uploads': uploads,
            'total': total,
            'limit': limit,
            'offset': offset
        }
    except Exception as e:
        return {'success': False, 'error': str(e), 'uploads': [], 'total': 0}


def delete_upload(filename):
    """
    Delete a specific uploaded WAV file.
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        dict: Delete result with success status
    """
    # Sanitize the filename
    safe_filename = sanitize_filename(filename)
    filepath = os.path.join(UPLOAD_DIR, safe_filename)
    
    if not os.path.exists(filepath):
        return {'success': False, 'error': 'File not found'}
    
    try:
        os.remove(filepath)
        return {'success': True, 'message': f'File "{safe_filename}" deleted successfully'}
    except Exception as e:
        return {'success': False, 'error': f'Deletion failed: {str(e)}'}


def get_checksum(filename):
    """
    Get MD5 checksum for a specific uploaded file.
    
    Args:
        filename: Name of the file
        
    Returns:
        dict: Checksum result
    """
    # Sanitize the filename
    safe_filename = sanitize_filename(filename)
    filepath = os.path.join(UPLOAD_DIR, safe_filename)
    
    if not os.path.exists(filepath):
        return {'success': False, 'error': 'File not found'}
    
    checksum = generate_checksum(filepath)
    if checksum.startswith('Error:'):
        return {'success': False, 'error': checksum}
    
    return {
        'success': True,
        'filename': safe_filename,
        'checksum': checksum
    }


def upload_wav():
    """
    Handle single WAV file upload with validation.
    
    Returns:
        dict: Upload result with file metadata
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    # Sanitize the filename
    original_filename = file.filename
    safe_filename = sanitize_filename(original_filename)
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({
            'success': False,
            'error': f'File too large (max {MAX_FILE_SIZE_MB}MB)',
            'file_size': file_size,
            'max_size': MAX_FILE_SIZE
        }), 400
    
    # Save the file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Extract base name without extension
    name_without_ext = os.path.splitext(safe_filename)[0]
    filename = f'{name_without_ext}_{timestamp}.wav'
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Save failed: {str(e)}'}), 500
    
    # Validate the WAV file
    validation_result = validate_wav_header(filepath)
    
    if not validation_result['valid']:
        # Delete the invalid file
        os.remove(filepath)
        return jsonify({
            'success': False,
            'error': validation_result['error'],
            'original_filename': original_filename,
            'saved_as': filename
        }), 400
    
    # Generate checksum
    checksum = generate_checksum(filepath)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'original_filename': original_filename,
        'filepath': filepath,
        'file_size': file_size,
        'checksum': checksum,
        'metadata': {
            'sample_rate': validation_result.get('sample_rate'),
            'num_channels': validation_result.get('num_channels'),
            'bits_per_sample': validation_result.get('bits_per_sample'),
            'duration_seconds': validation_result.get('duration_seconds')
        }
    }), 200


def upload_wav_batch():
    """
    Handle batch WAV file upload.
    
    Returns:
        dict: Batch upload results
    """
    if 'files' not in request.files:
        return jsonify({'success': False, 'error': 'No files part'}), 400
    
    files = request.files.getlist('files')
    
    if not files:
        return jsonify({'success': True, 'uploaded_count': 0, 'failed_count': 0})
    
    uploaded_count = 0
    failed_count = 0
    uploaded_files = []
    failed_files = []
    
    for file in files:
        if file.filename == '':
            failed_count += 1
            failed_files.append({'filename': '', 'error': 'Empty filename'})
            continue
        
        original_filename = file.filename
        safe_filename = sanitize_filename(original_filename)
        
        # Check file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            failed_count += 1
            failed_files.append({
                'filename': safe_filename,
                'error': f'File too large (max {MAX_FILE_SIZE_MB}MB)'
            })
            continue
        
        # Save the file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name_without_ext = os.path.splitext(safe_filename)[0]
        filename = f'{name_without_ext}_{timestamp}.wav'
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        try:
            file.save(filepath)
        except Exception as e:
            failed_count += 1
            failed_files.append({'filename': safe_filename, 'error': str(e)})
            continue
        
        # Validate the WAV file
        validation_result = validate_wav_header(filepath)
        
        if not validation_result['valid']:
            os.remove(filepath)
            failed_count += 1
            failed_files.append({
                'filename': safe_filename,
                'error': validation_result['error']
            })
            continue
        
        # Generate checksum
        checksum = generate_checksum(filepath)
        uploaded_count += 1
        uploaded_files.append({
            'filename': filename,
            'original_filename': safe_filename,
            'file_size': file_size,
            'checksum': checksum,
            'metadata': {
                'sample_rate': validation_result.get('sample_rate'),
                'num_channels': validation_result.get('num_channels'),
                'bits_per_sample': validation_result.get('bits_per_sample'),
                'duration_seconds': validation_result.get('duration_seconds')
            }
        })
    
    return jsonify({
        'success': True,
        'uploaded_count': uploaded_count,
        'failed_count': failed_count,
        'uploaded_files': uploaded_files,
        'failed_files': failed_files
    }), 200


def cleanup():
    """
    Cleanup endpoint to remove old uploaded files.
    
    Returns:
        dict: Cleanup results
    """
    max_age = request.json.get('max_age_hours', 24) if request.is_json else 24
    result = cleanup_old_uploads(max_age_hours=max_age)
    return jsonify(result), 200


# REST API Endpoints

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify(health_check())


@app.route('/upload_wav', methods=['POST'])
def route_upload_wav():
    """Single WAV file upload endpoint."""
    return upload_wav()


@app.route('/upload_wav_batch', methods=['POST'])
def route_upload_wav_batch():
    """Batch WAV file upload endpoint."""
    return upload_wav_batch()


@app.route('/uploads', methods=['GET'])
def list_uploads_endpoint():
    """List uploaded files with pagination."""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    result = list_uploads(limit=limit, offset=offset)
    return jsonify(result), 200 if result.get('success') else 400


@app.route('/uploads/delete/<filename>', methods=['DELETE'])
def delete_upload_endpoint(filename):
    """Delete a specific uploaded file."""
    result = delete_upload(filename)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 404


@app.route('/uploads/checksum/<filename>', methods=['GET'])
def get_checksum_endpoint(filename):
    """Get MD5 checksum for a file."""
    result = get_checksum(filename)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 404


@app.route('/cleanup', methods=['POST'])
def cleanup_endpoint():
    """Cleanup old uploaded files."""
    return cleanup()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
