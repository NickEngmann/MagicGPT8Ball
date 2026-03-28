# WAV Server API

## Overview
A Flask-based REST API for uploading and managing WAV audio recordings. Designed for use with the Magic 8 Ball ESP32-S3 project to handle voice recording uploads.

## Features
- WAV file upload with format validation
- File size limits and extension checking
- Automatic filename generation with timestamps
- SHA-256 hash calculation for file integrity
- JSON-based recordings index for tracking metadata
- RESTful API endpoints for CRUD operations

## Endpoints

### GET /
Returns API documentation and available endpoints.

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-28T07:08:52.123456",
  "upload_dir": "wav_uploads",
  "max_file_size_mb": 10
}
```

### POST /upload_wav
Upload a WAV file.

**Request:**
- Content-Type: `multipart/form-data`
- File field: `file` (required)

**Response on success (201):**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "filename": "My_Question_20260328_070852_123456.wav",
  "size_mb": 0.5,
  "hash": "a1b2c3d4e5f6..."
}
```

**Response on error (400):**
```json
{
  "success": false,
  "error": "Invalid file type: .mp3. Only WAV files allowed"
}
```

### GET /recordings
List all uploaded recordings.

**Response:**
```json
{
  "success": true,
  "count": 5,
  "recordings": [
    {
      "filename": "My_Question_20260328_070852_123456.wav",
      "original_filename": "question.wav",
      "size_mb": 0.5,
      "uploaded_at": "2026-03-28T07:08:52.123456",
      "filepath": "wav_uploads/My_Question_20260328_070852_123456.wav",
      "hash": "a1b2c3d4e5f6..."
    }
  ]
}
```

### GET /recordings/<filename>
Get information about a specific recording.

**Response:**
```json
{
  "success": true,
  "recording": { ... }
}
```

**Response on error (404):**
```json
{
  "success": false,
  "error": "Recording not found"
}
```

### DELETE /recordings/<filename>
Delete a recording by filename.

**Response on success (200):**
```json
{
  "success": true,
  "message": "Recording \"My_Question_20260328_070852_123456.wav\" deleted successfully"
}
```

**Response on error (404):**
```json
{
  "success": false,
  "error": "Recording not found"
}
```

## Configuration

### Environment Variables
- `UPLOAD_DIR`: Directory for storing uploaded files (default: `wav_uploads`)
- `MAX_FILE_SIZE_MB`: Maximum file size in MB (default: 10)
- `ALLOWED_EXTENSIONS`: Set of allowed file extensions (default: `{'.wav'}`)
- `RECORDINGS_INDEX_FILE`: Path to recordings index JSON file (default: `wav_uploads/recordings_index.json`)

### Server Configuration
```python
app.config['TESTING'] = True  # Enable for tests
app.run(host='0.0.0.0', port=5000, debug=True)
```

## File Validation

The server validates uploaded files by:
1. Checking file extension against allowed extensions
2. Verifying file size is within limits
3. Validating WAV file signature (RIFF header + WAVE format)
4. Calculating SHA-256 hash for integrity tracking

## Data Storage

- **WAV Files**: Stored in `wav_uploads/` directory
- **Metadata**: Stored in `wav_uploads/recordings_index.json`
- **Index Structure**:
  ```json
  {
    "recordings": [
      {
        "filename": "...",
        "filepath": "...",
        "original_filename": "...",
        "size_bytes": 0,
        "size_mb": 0.0,
        "uploaded_at": "...",
        "hash": "..."
      }
    ]
  }
  ```

## Testing

Run the test suite:
```bash
python3 -m pytest test/test_wav_server.py -v
```

All tests are written using pytest and cover:
- Upload validation (file type, size, format)
- Recording listing and management
- Health checks and API documentation
- Error handling and edge cases
- Index file corruption recovery
