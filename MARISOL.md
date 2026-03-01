# MARISOL.md — Pipeline Context

## Project Overview
The MagicGPT8Ball project is an IoT-enabled fortune-telling device powered by AI. It features voice recognition, motion sensing, and an OLED display. This repository contains both the ESP32 firmware (using PlatformIO) and a Python Flask server for uploading WAV audio files from the device to a backend service.

## Build & Run
- **Language**: Python 3.12
- **Framework**: Flask (for WAV upload server)
- **Docker image**: python:3.12-slim
- **Install deps**: `pip install flask` (for wav_server.py)
- **Run**: `python wav_server.py` (starts Flask server on port 5000)

## Testing
- **Test framework**: pytest
- **Test command**: `python -m pytest tests/ -v` (if tests exist)
- **Hardware mocks needed**: No (Flask server is pure Python)
- **Known test issues**: None identified

## Pipeline History
- Initial pipeline setup for WAV upload server
- Docker image: python:3.12-slim
- Dependencies: flask, pytest

## Known Issues
- None identified

## Notes
- wav_server.py provides a simple endpoint `/upload_wav` for POST requests
- Uploads are saved to `wav_uploads/` directory with timestamps
- The ESP32 firmware is built using PlatformIO (see platformio.ini)
