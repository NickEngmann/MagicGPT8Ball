"""
WAV File Upload Server for MagicGPT8Ball

Handles WAV file uploads with validation, batch processing,
checksum generation, and cleanup operations.
"""

from flask import Flask, request, jsonify
import os
import struct
import hashlib
from datetime import datetime
import re

app = Flask(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = 'wav_uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB default max file size


def validate_wav_header(file_path):
    """
    Validate that a file is a proper WAV file.
    
    Args:
        file_path: Path to the WAV file
        
    Returns:
        dict: Validation results with fields:
            - valid: bool indicating if file is valid
            - sample_rate: int if valid
            - num_channels: int if valid
            - bits_per_sample: int if valid
            - duration_seconds: float if valid
            - error: str if invalid (only present when invalid)
    """
    result = {
        'valid': False,
        'sample_rate': None,
        'num_channels': None,
        'bits_per_sample': None,
        'duration_seconds': None
    }
    
    try:
        with open(file_path, 'rb') as f:
            # Check minimum file size
            f.seek(0, 2)  # Seek to end
            file_size = f.tell()
            if file_size < 44:
                result['error'] = 'File too small to be a valid WAV (minimum 44 bytes)'
                return result
            
            f.seek(0)  # Reset to beginning
            
            # Read RIFF header
            riff_id = f.read(4)
            if riff_id != b'RIFF':
                result['error'] = 'Invalid RIFF header'
                return result
            
            # Read file size
            file_size_bytes = f.read(4)
            file_size = struct.unpack('<I', file_size_bytes)[0] + 8
            
            # Read WAV signature
            wav_id = f.read(4)
            if wav_id != b'WAVE':
                result['error'] = 'Invalid WAV signature'
                return result
            
            # Find fmt chunk
            fmt_chunk = False
            data_size = 0
            sample_rate = 0
            num_channels = 0
            bits_per_sample = 0
            
            while f.tell() < file_size - 8:
                chunk_id = f.read(4)
                chunk_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'fmt ':
                    fmt_chunk = True
                    if chunk_size >= 16:
                        audio_format = struct.unpack('<H', f.read(2))[0]
                        num_channels = struct.unpack('<H', f.read(2))[0]
                        sample_rate = struct.unpack('<I', f.read(4))[0]
                        byte_rate = struct.unpack('<I', f.read(4))[0]
                        block_align = struct.unpack('<H', f.read(2))[0]
                        bits_per_sample = struct.unpack('<H', f.read(2))[0]
                        
                        # Validate format (should be PCM)
                        if audio_format != 1:
                            result['error'] = f'Unsupported audio format: {audio_format}'
                            return result
                elif chunk_id == b'data':
                    data_size = chunk_size
                    break
                else:
                    # Skip unknown chunk
                    f.seek(chunk_size, 1)
            
            if not fmt_chunk:
                result['valid'] = False
                result['error'] = 'No fmt chunk found'
                return result
            
            # Calculate duration if we have data info
            duration = 0.0
            if num_channels > 0 and bits_per_sample > 0:
                duration = data_size / (sample_rate * num_channels * bits_per_sample / 8)
            
            result['valid'] = True
            result['sample_rate'] = sample_rate
            result['num_channels'] = num_channels
            result['bits_per_sample'] = bits_per_sample
            result['duration_seconds'] = duration
            
    except FileNotFoundError:
        result['valid'] = False
        result['error'] = 'File not found'
    except Exception as e:
        result['valid'] = False
        result['error'] = f'Error reading file: {str(e)}'
    
    return result


def generate_checksum(file_path):
    """
    Generate MD5 checksum for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: MD5 checksum as hexadecimal string
    """
    md5_hash = hashlib.md5()
    
    try:
        with open(file_path, 'rb') as f:
            # Read file in chunks for memory efficiency
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
        
        return md5_hash.hexdigest()
    
    except Exception as e:
        return f"Error: {str(e)}"


def cleanup_old_uploads(max_age_hours=24, min_size_bytes=44):
    """
    Clean up old WAV files from the upload directory.
    
    Args:
        max_age_hours: Maximum age of files to delete (default: 24 hours)
        min_size_bytes: Minimum valid WAV file size (default: 44 bytes)
        
    Returns:
        int: Number of files deleted
    """
    deleted_count = 0
    cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
    
    if not os.path.exists(UPLOAD_DIR):
        return 0
    
    for filename in os.listdir(UPLOAD_DIR):
        if filename.endswith('.wav'):
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            try:
                # Check file age
                file_mtime = os.path.getmtime(file_path)
                if file_mtime < cutoff_time:
                    # Check file size
                    file_size = os.path.getsize(file_path)
                    if file_size >= min_size_bytes:
                        os.remove(file_path)
                        deleted_count += 1
            except Exception as e:
                print(f"Error cleaning up {filename}: {str(e)}")
                continue
    
    return deleted_count


@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    """
    Handle single WAV file upload with validation.
    
    Expected form data:
        - file: WAV file (multipart/form-data)
        
    Returns JSON response with upload status, checksum, and metadata.
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file part in request'
        }), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No selected file'
        }), 400
    
    # Validate filename
    if not re.match(r'^[a-zA-Z0-9_\-\.]+\.wav$', file.filename):
        # Generate a safe filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f'recording_{timestamp}.wav'
    else:
        safe_filename = file.filename
    
    # Save the file
    filepath = os.path.join(UPLOAD_DIR, safe_filename)
    file.save(filepath)
    
    # Validate WAV header
    validation = validate_wav_header(filepath)

    if not validation['valid']:
        os.remove(filepath)
        error_msg = validation.get('error', 'Invalid WAV file')
        return jsonify({
            'success': False,
            'error': f'Invalid WAV file: {error_msg}',
            'validation': validation
        }), 400
    
    # Generate checksum
    checksum = generate_checksum(filepath)
    
    # Get file size
    file_size = os.path.getsize(filepath)
    
    # Get file modification time
    mtime = os.path.getmtime(filepath)
    mtime_str = datetime.fromtimestamp(mtime).isoformat()
    
    return jsonify({
        'success': True,
        'filename': safe_filename,
        'filepath': filepath,
        'checksum': checksum,
        'file_size': file_size,
        'metadata': {
            'sample_rate': validation['sample_rate'],
            'num_channels': validation['num_channels'],
            'bits_per_sample': validation['bits_per_sample'],
            'duration_seconds': validation['duration_seconds'],
            'upload_time': mtime_str
        }
    }), 200


@app.route('/upload_wav_batch', methods=['POST'])
def upload_wav_batch():
    """
    Handle batch WAV file upload.
    
    Expected form data:
        - files: List of WAV files (multipart/form-data)
        
    Returns JSON response with upload results for each file.
    """
    if 'files' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No files part in request',
            'uploaded': 0,
            'failed': 0,
            'files': []
        }), 400
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({
            'success': False,
            'error': 'No files selected',
            'uploaded': 0,
            'failed': 0,
            'files': []
        }), 400
    
    uploaded = 0
    failed = 0
    file_results = []
    
    for file in files:
        if file.filename == '':
            failed += 1
            file_results.append({
                'filename': '(empty)',
                'success': False,
                'error': 'No selected file'
            })
            continue
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        safe_filename = f'{file.filename.rsplit(".", 1)[0]}_{timestamp}.wav'
        
        filepath = os.path.join(UPLOAD_DIR, safe_filename)
        
        try:
            file.save(filepath)
            
            # Validate WAV header
            validation = validate_wav_header(filepath)

            if not validation['valid']:
                os.remove(filepath)
                failed += 1
                error_msg = validation.get('error', 'Invalid WAV file')
                file_results.append({
                    'filename': safe_filename,
                    'success': False,
                    'error': f'Invalid WAV: {error_msg}',
                    'validation': validation
                })
                continue
            
            # Generate checksum
            checksum = generate_checksum(filepath)
            file_size = os.path.getsize(filepath)
            
            uploaded += 1
            file_results.append({
                'filename': safe_filename,
                'filepath': filepath,
                'success': True,
                'checksum': checksum,
                'file_size': file_size,
                'metadata': {
                    'sample_rate': validation['sample_rate'],
                    'num_channels': validation['num_channels'],
                    'bits_per_sample': validation['bits_per_sample'],
                    'duration_seconds': validation['duration_seconds']
                }
            })
            
        except Exception as e:
            failed += 1
            file_results.append({
                'filename': safe_filename,
                'success': False,
                'error': f'Upload failed: {str(e)}'
            })
    
    return jsonify({
        'success': True,
        'uploaded': uploaded,
        'failed': failed,
        'total': uploaded + failed,
        'files': file_results
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring service status.
    
    Returns JSON response with service status and configuration.
    """
    upload_dir_exists = os.path.exists(UPLOAD_DIR)
    upload_dir_size = 0
    
    if upload_dir_exists:
        for root, dirs, files in os.walk(UPLOAD_DIR):
            for f in files:
                filepath = os.path.join(root, f)
                upload_dir_size += os.path.getsize(filepath)
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'upload_directory': UPLOAD_DIR,
        'upload_directory_exists': upload_dir_exists,
        'upload_directory_size_bytes': upload_dir_size,
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024)
    }), 200


@app.route('/uploads', methods=['GET'])
def list_uploads():
    """
    List all uploaded WAV files with pagination support.
    
    Query parameters:
        - limit: Maximum number of files to return (default: 50)
        - offset: Number of files to skip (default: 0)
        
    Returns JSON response with list of uploaded files.
    """
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
    
    all_files = []
    for filename in os.listdir(UPLOAD_DIR):
        if filename.endswith('.wav'):
            filepath = os.path.join(UPLOAD_DIR, filename)
            try:
                file_stat = os.stat(filepath)
                all_files.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    'created': datetime.fromtimestamp(file_stat.st_ctime).isoformat()
                })
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue
    
    # Sort by creation time, newest first
    all_files.sort(key=lambda x: x['created'], reverse=True)
    
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


@app.route('/uploads/delete/<filename>', methods=['DELETE'])
def delete_upload(filename):
    """
    Delete a specific uploaded WAV file.
    
    Args:
        filename: Name of the file to delete
        
    Returns JSON response with deletion status.
    """
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(filepath):
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404
    
    try:
        os.remove(filepath)
        return jsonify({
            'success': True,
            'message': f'File {filename} deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete file: {str(e)}'
        }), 500


@app.route('/cleanup', methods=['POST'])
def cleanup():
    """
    Clean up old uploaded files.
    
    Query parameters:
        - max_age_hours: Maximum file age in hours (default: 24)
        
    Returns JSON response with cleanup results.
    """
    max_age = int(request.args.get('max_age_hours', 24))
    
    deleted_count = cleanup_old_uploads(max_age_hours=max_age)
    
    return jsonify({
        'success': True,
        'message': f'Cleaned up {deleted_count} old file(s)',
        'deleted_count': deleted_count,
        'max_age_hours': max_age
    }), 200


@app.route('/uploads/checksum/<filename>', methods=['GET'])
def get_file_checksum(filename):
    """
    Get MD5 checksum of an uploaded file.
    
    Args:
        filename: Name of the file
        
    Returns JSON response with checksum.
    """
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(filepath):
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404
    
    checksum = generate_checksum(filepath)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'checksum': checksum
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
