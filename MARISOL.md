# MARISOL.md — Pipeline Context for MagicGPT8Ball

## Pipeline History
- *2026-03-28* — Implementation Complete: All Python tests are already complete and passing with 22 tests in test_wav_server.py covering Flask WAV upload server functionality, file validation, recording management, and error handling.

- *2026-03-28* — Test Execution: Successfully ran pytest on test/test_wav_server.py, all 22 tests passed with 0 failures in 0.14s execution time.

- *2026-03-28* — Repository Analysis: Completed documentation update task, analyzing project structure, test suites, and Python components for MagicGPT8Ball ESP32-S3 IoT project.

- *2026-03-26* — Initial Setup: Project repository created with PlatformIO configuration for waveshare_esp32_s3 board, including LVGL graphics library, WiFiManager, and ArduinoJson dependencies.

## Test Results Summary

### Python Test Suite
| Test File | Tests | Status | Coverage |
|-----------|-------|--------|----------|
| test/test_wav_server.py | 22 | All Passed | Upload validation, recording management, API endpoints, error handling |

### Test Categories Covered
- WAV file upload validation (file type, size, format)
- Recording list/get/delete operations
- Health check and API documentation endpoints
- Index file corruption recovery
- Case-insensitive file extension handling
- SHA-256 hash calculation verification

## Build Configuration
- **Platform**: espressif32@6.5.0
- **Board**: waveshare_esp32_s3
- **Framework**: Arduino
- **Display**: 240×240 Round LCD (TFT_eSPI + LVGL 8.3.8)
- **Microphone**: MAX9814 ADC (GPIO2, 32kHz mono)
- **IMU**: QMI8658 6-axis (I2C GPIO6/GPIO7)
- **Storage**: LittleFS
- **Dependencies**: WiFiManager, ArduinoJson 7.2.1, Adafruit NeoPixel 1.12.0

## API Services
- **Voice Transcription**: OpenAI Whisper API (via val.town endpoint)
- **AI Responses**: ChatGPT (via val.town endpoint)
- **File Upload Server**: Flask-based WAV server (wav_server.py)

## Project Structure
```
MagicGPT8Ball/
├── src/
│   ├── main.cpp                    # Main ESP32 application
│   ├── Animations.*               # LVGL animation manager
│   ├── Recorder.*                 # Audio recording implementation
│   ├── TextStateManager.*         # Display state management
│   ├── VibrationManager.*         # Haptic feedback control
│   └── LEDLogger.*                # RGB LED status indicators
├── lib/
│   ├── lvgl/                      # LVGL 8.3.8 graphics library
│   ├── TFT_eSPI/                  # Display driver
│   ├── TFT_eSPI_Setups/           # ESP32-S3 board setup
│   └── QMI8658/                   # IMU driver
├── test/
│   └── test_wav_server.py         # Flask server unit tests (22 tests)
├── tests/
│   └── conftest.py                # Pytest fixtures
├── wav_server.py                  # REST API for WAV file handling
└── platformio.ini                 # Build configuration
```

## Dependencies (from platformio.ini)
- https://github.com/tzapu/WiFiManager.git
- bblanchon/ArduinoJson @ ^7.2.1
- adafruit/Adafruit NeoPixel @ ^1.12.0
- LVGL 8.3.8
- TFT_eSPI
- QMI8658
