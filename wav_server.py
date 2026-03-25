from flask import Flask, request, jsonify
import os
import struct
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = 'wav_uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


def validate_wav_header(file_path: str) -> Dict[str, Any]:
    """
    Validate WAV file header and return metadata.
    
    Returns a dictionary with validation results and metadata.
    """
    try:
        with open(file_path, 'rb') as f:
            # Read first 44 bytes (standard WAV header)
            header = f.read(44)
            
            if len(header) < 44:
                return {
                    'valid': False,
                    'error': 'File too small to be a valid WAV file'
                }
            
            # Check RIFF signature
            if header[:4] != b'RIFF':
                return {
                    'valid': False,
                    'error': 'Invalid RIFF signature'
                }
            
            # Check WAV signature
            if header[8:12] != b'WAVE':
                return {
                    'valid': False,
                    'error': 'Invalid WAV signature'
                }
            
            # Find fmt chunk
            format_found = False
            data_found = False
            sample_rate = 0
            num_channels = 0
            bits_per_sample = 0

            offset = 12
            while offset <= len(header) - 8:  # Need at least 8 more bytes for chunk header
                chunk_id = header[offset:offset+4].decode('ascii', errors='ignore')
                chunk_size = struct.unpack('<I', header[offset+4:offset+8])[0]

                if chunk_id == 'fmt ':
                    format_found = True
                    if chunk_size >= 16:
                        # fmt chunk format: chunk_id(4) + size(4) + audio_format(2) + num_channels(2) + sample_rate(4) + byte_rate(4) + block_align(2) + bits_per_sample(2)
                        audio_format = struct.unpack('<H', header[offset+8:offset+10])[0]
                        num_channels = struct.unpack('<H', header[offset+10:offset+12])[0]
                        sample_rate = struct.unpack('<I', header[offset+12:offset+16])[0]
                        byte_rate = struct.unpack('<I', header[offset+16:offset+20])[0]
                        block_align = struct.unpack('<H', header[offset+20:offset+22])[0]
                        bits_per_sample = struct.unpack('<H', header[offset+22:offset+24])[0]
                elif chunk_id == 'data':
                    data_found = True
                    break

                offset += 8 + chunk_size
                if offset >= len(header):
                    break
            
            if not format_found:
                return {
                    'valid': False,
                    'error': 'No fmt chunk found'
                }
            
            if not data_found:
                return {
                    'valid': False,
                    'error': 'No data chunk found'
                }
            
            # Calculate file duration in seconds
            f.seek(0, 2)  # Seek to end
            file_size = f.tell()
            data_size = file_size - 44
            
            # Calculate bytes per second
            bytes_per_second = sample_rate * num_channels * bits_per_sample // 8
            
            if bytes_per_second == 0:
                return {
                    'valid': False,
                    'error': 'Invalid audio format parameters'
                }
            
            audio_duration = data_size / bytes_per_second if data_size > 0 else 0
            
            return {
                'valid': True,
                'sample_rate': sample_rate,
                'num_channels': num_channels,
                'bits_per_sample': bits_per_sample,
                'duration_seconds': round(audio_duration, 2),
                'file_size_bytes': file_size,
                'data_size_bytes': data_size
            }
            
    except Exception as e:
        logger.error(f"Error validating WAV file: {str(e)}")
        return {
            'valid': False,
            'error': f'Validation error: {str(e)}'
        }


def generate_checksum(file_path: str) -> str:
    """Generate MD5 checksum for a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def cleanup_old_uploads(max_age_hours: int = 24) -> int:
    """
    Clean up old WAV files older than specified hours.
    Returns the number of files deleted.
    """
    deleted_count = 0
    cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
    
    for file_path in Path(UPLOAD_DIR).glob('*.wav'):
        file_mtime = file_path.stat().st_mtime
        if file_mtime < cutoff_time:
            try:
                file_path.unlink()
                deleted_count += 1
                logger.info(f"Deleted old upload: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to delete {file_path.name}: {str(e)}")
    
    return deleted_count


@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    """
    Handle WAV file upload with validation.
    
    Expected: multipart form data with 'file' field
    Returns: JSON response with upload status and file metadata
    """
    if 'file' not in request.files:
        logger.warning("Upload request without file part")
        return jsonify({
            'success': False,
            'error': 'No file part in request'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("Upload request with empty filename")
        return jsonify({
            'success': False,
            'error': 'No selected file'
        }), 400
    
    # Check file extension
    if not file.filename.lower().endswith('.wav'):
        logger.warning(f"Invalid file extension: {file.filename}")
        return jsonify({
            'success': False,
            'error': 'File must be a WAV file'
        }), 400
    
    # Check file size before saving
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
        return jsonify({
            'success': False,
            'error': f'File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f} MB'
        }), 400
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = hashlib.md5(str(timestamp + str(file_size)).encode()).hexdigest()[:8]
    filename = f'recording_{timestamp}_{unique_id}.wav'
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    try:
        # Save the file
        file.save(filepath)
        logger.info(f"Saved file: {filepath} ({file_size} bytes)")
        
        # Validate WAV header
        validation_result = validate_wav_header(filepath)
        
        if not validation_result['valid']:
            # Remove invalid file
            os.remove(filepath)
            logger.warning(f"Invalid WAV file: {filepath} - {validation_result.get('error')}")
            return jsonify({
                'success': False,
                'error': f'Invalid WAV file: {validation_result.get("error")}'
            }), 400
        
        # Calculate file checksum
        checksum = generate_checksum(filepath)
        
        logger.info(f"File validated successfully: {validation_result}")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'file_size': file_size,
            'checksum': checksum,
            'metadata': {
                'sample_rate': validation_result['sample_rate'],
                'channels': validation_result['num_channels'],
                'bits_per_sample': validation_result['bits_per_sample'],
                'duration_seconds': validation_result['duration_seconds']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        # Clean up partial file if it exists
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass
        return jsonify({
            'success': False,
            'error': f'Upload processing error: {str(e)}'
        }), 500


@app.route('/upload_wav_batch', methods=['POST'])
def upload_wav_batch():
    """
    Handle batch WAV file uploads.
    
    Expected: multipart form data with 'files' field (multiple files)
    Returns: JSON response with batch upload status
    """
    if 'files' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No files in request'
        }), 400
    
    files = request.files.getlist('files')
    results = {
        'success': True,
        'uploaded': 0,
        'failed': 0,
        'files': []
    }
    
    for file in files:
        if file.filename == '':
            continue
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'{file.filename.rsplit(".", 1)[0]}_{timestamp}.wav'
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        try:
            file.save(filepath)
            validation_result = validate_wav_header(filepath)
            
            if validation_result['valid']:
                checksum = generate_checksum(filepath)
                results['uploaded'] += 1
                results['files'].append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': validation_result['file_size_bytes'],
                    'checksum': checksum,
                    'metadata': {
                        'sample_rate': validation_result['sample_rate'],
                        'channels': validation_result['num_channels'],
                        'duration_seconds': validation_result['duration_seconds']
                    },
                    'success': True
                })
            else:
                os.remove(filepath)
                results['failed'] += 1
                results['files'].append({
                    'filename': filename,
                    'success': False,
                    'error': validation_result['error']
                })
        except Exception as e:
            results['failed'] += 1
            results['files'].append({
                'filename': filename,
                'success': False,
                'error': str(e)
            })
    
    status_code = 200 if results['failed'] == 0 else 207  # Partial Success
    return jsonify(results), status_code


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'upload_directory': UPLOAD_DIR,
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024)
    }), 200


@app.route('/uploads', methods=['GET'])
def list_uploads():
    """
    List all uploaded WAV files with metadata.
    
    Query parameters:
        - limit: Maximum number of files to return (default: 100)
        - offset: Number of files to skip (default: 0)
    """
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        uploads = []
        for file_path in sorted(Path(UPLOAD_DIR).glob('*.wav'), 
                                key=lambda x: x.stat().st_mtime, 
                                reverse=True):
            if len(uploads) >= offset + limit:
                break
            
            try:
                stat = file_path.stat()
                validation_result = validate_wav_header(str(file_path))
                
                uploads.append({
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size_bytes': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'metadata': validation_result.get('metadata', {}) if validation_result.get('valid') else {}
                })
            except Exception as e:
                logger.error(f"Error processing file {file_path.name}: {str(e)}")
                continue
        
        # Apply offset
        uploads = uploads[offset:]
        
        return jsonify({
            'success': True,
            'uploads': uploads,
            'total': len(uploads),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing uploads: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/uploads/delete/<filename>', methods=['DELETE'])
def delete_upload(filename: str):
    """Delete a specific uploaded file."""
    try:
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        os.remove(filepath)
        logger.info(f"Deleted file: {filepath}")
        
        return jsonify({
            'success': True,
            'message': f'File {filename} deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/cleanup', methods=['POST'])
def cleanup():
    """
    Clean up old uploads automatically.
    
    Query parameters:
        - max_age_hours: Age threshold for deletion (default: 24)
    """
    try:
        max_age_hours = int(request.args.get('max_age_hours', 24))
        deleted_count = cleanup_old_uploads(max_age_hours)
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'max_age_hours': max_age_hours
        }), 200
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
