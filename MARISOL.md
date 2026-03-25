# MARISOL.md — Pipeline Context for MagicGPT8Ball

## Project Information

**Project**: Magic (GPT)8 Ball — ESP32-S3 IoT device with voice recognition, AI responses, and LVGL display  
**Framework**: PlatformIO with Arduino framework  
**Docker Image**: lotus-platformio:latest  
**Primary Language**: C++ (ESP32 Arduino), Python (server tools)  
**Board**: waveshare_esp32_s3 (1.28" Round LCD 240×240)  
**PlatformIO Platform**: espressif32@6.5.0  
**LVGL Version**: 7.x or 8.x (compatible)

## Dependencies

**PlatformIO Libraries** (from platformio.ini):
- WiFiManager (https://github.com/tzapu/WiFiManager.git) — Network configuration
- ArduinoJson @ ^7.2.1 (bblanchon/ArduinoJson) — JSON parsing
- Adafruit NeoPixel @ ^1.12.0 — RGB LED control

**Python Dependencies** (from wav_server.py, test files):
- flask — Web server for WAV uploads
- pytest — Test framework
- pillow (PIL) — Image processing for SJPG conversion
- serial — ESP32 communication

## Test Results

### Python Tests (tests/)

| Test File | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| test_wav_server.py | 24 | WAV upload server | 24/24 passed |
| test_jpg_to_sjpg.py | 20 | SJPG conversion | 20/20 passed |
| **Total Python** | **44** | **All Python tests** | **44/44 passed** |

**Test Coverage Summary**:
- WAV header validation and file uploads
- Flask endpoint testing (upload, batch, health, list, delete, cleanup)
- Image conversion validation
- SJPG header and C array generation
- Memory and cleanup operations

### C++ Native Tests (test/test_native/)

| Test File | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| test_placeholder.c | 1 | Unity smoke test | 1/1 passed |

**Note**: C++ Unity tests require PlatformIO native testing framework setup.

## Pipeline History

- **2026-03-25** — Implement: Successfully created comprehensive Python test suites covering wav_server.py and jpg_to_sjpg_enhanced.py conversion scripts with 44 tests passing, including integration tests, unit tests for WAV header validation, checksum generation, upload endpoints, batch processing, image validation, and SJPG header creation.

- **2026-03-25** — Implement: Created test_wav_server.py with full Flask endpoint coverage including upload_wav, upload_wav_batch, health check, list uploads with pagination, file deletion, and cleanup operations, along with test_jpg_to_sjpg.py for image processing workflows.

## Build Configuration

**platformio.ini Key Settings**:
- Monitor Speed: 115200
- Filesystem: LittleFS
- Library Mode: chain
- Build Cache: .pio/build_cache
- Pre-build Script: generate_env.py

## Environment Setup

**Required Environment Variables** (see .env.example):
- VALTOWN_URL — Serverless API endpoint
- DEVICE_TOKEN — Authentication token

**Setup Script**: generate_env.py — Copies .env to LittleFS during build

## Component Overview

### C++ Components (src/)

| Component | Description |
|-----------|-------------|
| main.cpp | Application entry point, WiFi/HTTP handling, recording flow |
| Recorder.h/cpp | Audio capture with voice detection, ADC management |
| Animations.h/cpp | LVGL triangle display, gyro positioning, idle motion |
| TextStateManager.h | Display text transitions, state machine |
| LEDLogger.h/cpp | WS2812B RGB LED state indicator |
| VibrationManager.h | Dual motor haptic feedback control |
| Environment.h | LittleFS .env loading and access |

### Python Components

| Component | Description |
|-----------|-------------|
| wav_server.py | Flask server for WAV upload validation and processing |
| generate_env.py | PlatformIO pre-build script for .env deployment |
| test_wav_server.py | Unit and integration tests for wav_server.py |
| test_jpg_to_sjpg.py | Tests for LVGL SJPG image conversion |
| tests/conftest.py | pytest fixtures for PlatformIO environment |

## Hardware Specifications

- **Microcontroller**: ESP32-S3 (Waveshare board)
- **Display**: 1.28" Round LCD (240×240) via SPI
- **IMU**: QMI8658 6-axis (I2C)
- **Audio**: MAX9814 microphone amplifier (ADC1_CH1/GPIO2)
- **LED**: WS2812B RGB (GPIO3)
- **Vibration**: 2x DC motors (GPIO5, GPIO13)
- **Storage**: LittleFS for .env persistence
- **PSRAM**: Enabled for buffer allocation

## Wiring Summary

| Component | Connection |
|-----------|------------|
| LCD DC | GPIO8 |
| LCD CS | GPIO9 |
| LCD CLK | GPIO10 |
| LCD MOSI | GPIO11 |
| LCD RST | GPIO12 |
| LCD BL | GPIO40 |
| IMU SDA | GPIO6 |
| IMU SCL | GPIO7 |
| Mic OUT | GPIO2 |
| LED | GPIO3 |
| Vib Motor 1 | GPIO5 |
| Vib Motor 2 | GPIO13 |

## API Endpoints (wav_server.py)

| Endpoint | Method | Description |
|----------|--------|-------------|
| /upload_wav | POST | Single WAV upload with validation |
| /upload_wav_batch | POST | Batch WAV upload |
| /health | GET | Health check |
| /uploads | GET | List uploaded files (with pagination) |
| /uploads/delete/<filename> | DELETE | Delete specific file |
| /cleanup | POST | Clean old uploads |

## Project Structure

```
MagicGPT8Ball/
├── src/                     # C++ Arduino source
│   ├── main.cpp            # Main application
│   ├── Recorder.*          # Audio recording
│   ├── Animations.*        # LVGL display
│   ├── TextStateManager.h  # UI text state
│   ├── VibrationManager.h  # Haptic feedback
│   ├── LEDLogger.*         # RGB LED
│   └── Environment.h       # Config loader
├── lib/                    # PlatformIO libraries
│   ├── lvgl/              # LVGL graphics
│   ├── TFT_eSPI/          # Display driver
│   ├── QMI8658/           # IMU driver
│   └── TFT_eSPI_Setups/   # Board setup
├── test/test_native/       # C++ Unity tests
├── test/test_lvgl_render/  # LVGL headless test helper
├── tests/                  # Python pytest tests
│   ├── test_wav_server.py
│   ├── test_jpg_to_sjpg.py
│   └── conftest.py
├── wav_server.py          # Flask upload server
├── generate_env.py        # Build script
├── platformio.ini         # Build configuration
├── .env.example           # Environment template
└── data/                  # Built filesystem (LittleFS)
```
