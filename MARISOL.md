# MARISOL.md — Pipeline Context

## Project Overview
The Magic (GPT)8 Ball is an IoT fortune-telling device built on ESP32-S3 hardware using PlatformIO and Arduino framework. It features voice recognition via microphone array, motion sensing with QMI8658 accelerometer, LVGL-based graphical display, and AI-powered responses via OpenAI ChatGPT and Whisper APIs. The device connects to WiFi and communicates with a Flask-based WAV server for audio processing.

## Build & Run
- **Language**: C++ (Arduino framework)
- **Framework**: PlatformIO
- **Docker image**: python:3.12-slim
- **Install deps**: pip install --no-cache-dir platformio pytest
- **Run**: No runnable entry point — this is embedded hardware firmware. Build with: `pio run`. Upload to device with: `pio run -t upload`

## Testing
- **Test framework**: pytest (for Python components)
- **Test command**: python -m pytest tests/ -v (if tests directory exists)
- **Hardware mocks needed**: yes — ESP32-S3 hardware, QMI8658 accelerometer, microphone array, display
- **Known test issues**: Cannot run full hardware tests in container environment. Python scripts (wav_server.py, generate_env.py) can be tested separately.

## Pipeline History
- Initial project setup with PlatformIO ESP32-S3 configuration
- Added LVGL graphics library integration
- Integrated WiFiManager for network configuration
- Added OpenAI API integration for voice recognition and responses
- Created wav_server.py Flask server for audio file handling
- Added generate_env.py for environment variable management

## Known Issues
- Hardware-dependent functionality cannot be fully tested in CI environment
- Requires physical ESP32-S3 board with specific peripherals (QMI8658, display, microphone)
- OpenAI API keys required for full functionality
- WAV server requires separate Python environment to run

## Notes
- Board configuration: waveshare_esp32_s3 (2.9 inch display)
- Key libraries: WiFiManager, ArduinoJson, Adafruit NeoPixel, LVGL, TFT_eSPI, QMI8658
- Data directory structure: data/.env contains environment variables for build
- wav_server.py runs on port 5000 for audio file uploads
- generate_env.py copies .env or .env.example to data directory during build
- Main source file: src/main.cpp (16KB, handles all device logic)
- Animation system: src/Animations.cpp (8KB, handles display animations)
- Voice recorder: src/Recorder.h/cpp (handles microphone input)
- Text state manager: src/TextStateManager.h (manages fortune text display)
- Vibration manager: src/VibrationManager.h (handles haptic feedback)
- val.town integration: src/val.town.js (serverless hosting reference)
