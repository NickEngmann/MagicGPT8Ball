# MARISOL.md — Pipeline Context

## Project Overview
Magic (GPT)8 Ball is an IoT fortune-telling device built on ESP32-S3 hardware using PlatformIO and Arduino framework. It features voice recognition, motion sensing, and real-time AI responses through ChatGPT. The device uses a circular 240×240 display, QMI8658 6-axis IMU for motion detection, MAX9814 microphone for audio capture, and communicates via WiFi with external APIs.

## Build & Run
- **Language**: C++ (Arduino framework)
- **Framework**: PlatformIO, ESP32 Arduino core
- **Docker image**: platformio/platformio-arduino:latest (Ubuntu-based PlatformIO image)
- **Install deps**: `pip install --no-cache-dir platformio` then `pio install` (installs Arduino libraries via lib_deps in platformio.ini)
- **Run**: No runnable entry point — this is embedded hardware firmware. Build with `pio run`, upload to ESP32-S3 device via `pio run --target upload` or `pio upload`

## Testing
- **Test framework**: None (hardware-dependent embedded project)
- **Test command**: No automated tests available — project requires physical ESP32-S3 hardware with QMI8658 sensor, microphone array, and TFT display
- **Hardware mocks needed**: Yes — requires ESP32-S3, QMI8658 accelerometer, 320x240 SPI TFT display, I2S microphone array
- **Known test issues**: Cannot run tests in container environment; requires physical hardware for any validation. The tests/ directory is empty.

## Pipeline History
- 2024-03-10: Initial pipeline run confirmed project structure with PlatformIO build system and ESP32-S3 target
- 2024-03-10: Verified no automated tests exist in tests/ directory; only LVGL library test files found in lib/
- 2024-03-10: Confirmed hardware dependencies: QMI8658 IMU, MAX9814 microphone, WS2812B RGB LED, vibration motors, 1.28" round LCD
- 2024-03-10: Verified environment configuration requires .env file with VALTOWN_URL and DEVICE_TOKEN for API communication
- 2024-03-10: Confirmed build uses waveshare_esp32_s3 environment from platformio.ini with LittleFS filesystem upload

## Known Issues
- No automated testing possible without hardware
- Requires external API keys (OpenAI, val.town) for full functionality
- Hardware dependencies: QMI8658 sensor, I2S microphone, 1.28" TFT display, vibration motors, RGB LED
- PlatformIO build requires ESP32 Arduino core installed
- .env file required for operation (contains API credentials)
- Cannot verify functionality in container environment

## Notes
- **Architecture**: Embedded firmware with hardware abstraction layers for sensors, display, and audio
- **Key files**: src/main.cpp (entry point), src/Recorder.h (audio capture), src/Animations.h (display), src/VibrationManager.h (haptics)
- **Libraries**: LVGL for UI, TFT_eSPI for display driver, WiFiManager for network config, ArduinoJson for API
- **Build targets**: `pio run` builds firmware, `pio run -t uploadfs` uploads LittleFS filesystem, `pio run -t upload` uploads firmware
- **Debugging**: Enable debug mode by uncommenting `#define ENABLE_DEBUG` in Recorder.h and main.cpp
- **Environment setup**: Copy .env to data/ directory during build via generate_env.py script
