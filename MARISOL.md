# MARISOL.md — Pipeline Context

## Project Overview
MagicGPT8Ball is an IoT fortune-telling device built on ESP32-S3 hardware using PlatformIO/Arduino framework. The firmware implements voice recording, motion sensing (QMI8658 IMU), real-time audio transcription via OpenAI Whisper, and AI responses through ChatGPT. The device features a 1.28" round LCD display, haptic feedback, and WiFi connectivity. A supporting Python Flask server (wav_server.py) handles WAV file uploads from the device for audio processing.

## Build & Run
- **Language**: C++ (Arduino framework), Python 3.x (supporting tools)
- **Framework**: PlatformIO/ESP32, Flask (wav_server.py only)
- **Docker image**: python:3.12-slim (for wav_server.py only)
- **Install deps (ESP32)**: pio lib install (PlatformIO)
- **Install deps (wav_server)**: pip install flask
- **Run (ESP32)**: pio run --target upload (build and flash to hardware)
- **Run (wav_server)**: python wav_server.py (starts on 0.0.0.0:5000)

## Testing
- **Test framework**: None currently (no pytest tests in repository)
- **Test command**: N/A - no automated tests present
- **Hardware mocks needed**: yes - ESP32-S3 hardware required for firmware testing
- **Known test issues**: No test suite exists; hardware testing required for firmware validation

## Pipeline History
- Initial setup: PlatformIO ESP32-S3 firmware project created for MagicGPT8Ball
- PR #45: Added wav_server.py supporting tool for audio file uploads
- Build target: waveshare_esp32_s3 board with LittleFS filesystem

## Known Issues
- No automated test suite for firmware or wav_server.py
- Hardware testing required for all firmware changes
- No requirements.txt file (dependencies installed via PlatformIO and pip)

## Notes
- wav_server.py creates 'wav_uploads' directory automatically if it doesn't exist
- Server listens on port 5000 by default for WAV file uploads
- ESP32-S3 hardware (waveshare_esp32_s3 board) uploads audio files to wav_server.py
- PlatformIO uses custom build script (generate_env.py) to copy .env to device filesystem
- Board configuration: espressif32@6.5.0, LittleFS filesystem, 115200 baud monitor
- Key libraries: WiFiManager, ArduinoJson 7.x, LVGL, TFT_eSPI, Adafruit NeoPixel, QMI8658 IMU driver
- wav_server.py is a supporting tool, not the primary build artifact
