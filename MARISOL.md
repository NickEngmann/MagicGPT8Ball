# MARISOL.md — Pipeline Context for MagicGPT8Ball

## Project Overview
ESP32-S3 based IoT Magic 8 Ball with voice recognition, AI responses, and LVGL display using PlatformIO.



## Build & Run
- **Language**: cpp
- **Framework**: platformio
- **Docker image**: gcc:14
- **Install deps**: (none)
- **Run**: (see source code)



## Testing
- **Test framework**: pytest (Python 3.12.3, pytest 7.4.4, pytest-cov 7.0.0)
- **Test command**: `make test`, `pytest test/ -v`, or `python3 test_runner.py`
- **Hardware mocks needed**: yes (embedded_c)
- **Last result**: 132/132 passed (100% pass rate)



## Pipeline History
- *2026-03-19* — Pipeline context initialized. MARISOL.md created to document repository structure, dependencies, and build configuration.
- *2026-03-17* — Project source code committed. Main components include Animations, Recorder, TextStateManager, VibrationManager, LEDLogger, and Environment modules.
- *2026-03-17* — PlatformIO configuration established with espressif32@6.5.0 platform and waveshare_esp32_s3 board.
- *2026-03-21* — Implemented comprehensive Python test suite for the MagicGPT8Ball ESP32-S3 IoT project with 85 tests covering all major modules.
- *2026-03-25* — Test suite expanded to 132 tests including integration tests, unit tests, and C++ native tests. All tests pass with 100% success rate.

## Notes
- Project requires OpenAI API integration via val.town serverless endpoint
- Environment variables: VALTOWN_URL and DEVICE_TOKEN (configured via .env file)
- Default timeout for WiFi captive portal: 180 seconds (source: src/main.cpp, line 334)
- Response display duration: 7000ms (source: src/main.cpp, line 32)
- Shake detection threshold: 5000.0f G-force (source: src/main.cpp, line 32)
- Serial monitor speed: 115200 baud (source: platformio.ini, line 17)



## Repository Analysis

**Project:** ESP32-S3 based IoT Magic 8 Ball with voice recognition, AI responses, and LVGL display using PlatformIO

**Hardware Board:** waveshare_esp32_s3
- ESP32-S3 microcontroller (240MHz)
- 16MB Flash memory
- 8MB PSRAM (Quad SPI)
- 1.28" Round LCD Display (240×240 resolution)
- Built-in QMI8658 6-axis IMU
- USB-C interface

**Framework:** Arduino (espidf also supported)

**Library Dependencies:**
1. WiFiManager (https://github.com/tzapu/WiFiManager.git) — lines 19, platformio.ini
2. ArduinoJson ^7.2.1 (bblanchon/ArduinoJson) — lines 20, platformio.ini
3. Adafruit NeoPixel ^1.12.0 — lines 21, platformio.ini
4. Custom libraries in lib/ directory:
   - lib/lvgl — LVGL graphics library
   - lib/TFT_eSPI — TFT display driver
   - lib/TFT_eSPI_Setups — Display setup configurations
   - lib/QMI8658 — IMU driver

**Audio Configuration:**
- Sample Rate: 32000 Hz (source: src/Recorder.h, line 10)
- Channels: Mono (line 11)
- Bits Per Sample: 16 (line 12)
- ADC Channel: GPIO2/ADC1_CHANNEL_1 (lines 24-25)
- MAX9814 Microphone Amplifier
- Maximum Recording Duration: 10 seconds (line 23)

**Pin Configuration:**
- LCD: DC=GPIO8, CS=GPIO9, CLK=GPIO10, MOSI=GPIO11, RST=GPIO12, BL=GPIO40
- IMU (QMI8658): SDA=GPIO6, SCL=GPIO7
- Microphone (ADC): GPIO2
- RGB LED: GPIO3
- Vibration Motors: GPIO5, GPIO13
- Motor Driver Pins: 45, 46 (source: src/main.cpp, line 18)




## Build System

**Primary Build Tool:** PlatformIO

**Build Commands:**
- pio run --target upload — Build and upload firmware
- pio run -t uploadfs — Upload filesystem
- pio lib install — Install library dependencies

**Custom Build Scripts:**
- generate_env.py (source: platformio.ini, line 25) — Pre-build script that copies .env or .env.example to data directory
- LittleFS filesystem integration

**Memory Configuration:**
- PSRAM: 8MB Quad SPI (source: boards/waveshare_esp32_s3.json, line 3)
- Flash size: 16MB (source: boards/waveshare_esp32_s3.json, line 37)
- Partitions: default_8MB.csv




## Test Status

**Test Framework:** pytest (Python 3.12.3, pytest 7.4.4, pytest-cov 7.0.0)

**Python Test Suite:**
- Total Tests: 132 passed
- test_environment_py.py: 15 tests
- test_integration_py.py: 48 tests
- test_integration_py_test.py: 48 tests
- test_led_logger_py.py: 9 tests
- test_native_tests.py: 18 tests (verification)
- test_recorder_py.py: 9 tests
- test_text_state_manager_py.py: 16 tests
- test_vibration_manager_py.py: 9 tests

**C++ Native Tests (Unity Framework):**
- test_native/test_environment.c: 9 tests
- test_native/test_recorder.c: 11 tests
- test_native/test_vibration_manager.c: 9 tests
- test_native/test_led_logger.c: 11 tests
- test_native/test_text_state_manager.c: 11 tests
- test_native/test_wav_upload.c: 12 tests

**Test Command:** `make test`, `pytest test/ -v`, or `python3 test_runner.py`
**Current Status:** 132 Python tests passed (100% pass rate)
**Integration:** Tests use mocked implementations to avoid hardware dependencies

